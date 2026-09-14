import os
import re
import sys
import zipfile
import tempfile

import django


# -------------------------------------------------
# Django setup
# -------------------------------------------------

PROJECT_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


from django.core.files import File
from portal.models import Lesson, VideoLesson


# -------------------------------------------------
# ZIP file location
# -------------------------------------------------

ZIP_FILE = r"D:\Intermediate Lessons A.V.zip"


# -------------------------------------------------
# Check ZIP
# -------------------------------------------------

if not os.path.exists(ZIP_FILE):
    print("ERROR: ZIP file not found:")
    print(ZIP_FILE)
    sys.exit()


# -------------------------------------------------
# Extract ZIP
# -------------------------------------------------

with tempfile.TemporaryDirectory() as temp_folder:

    print("Extracting Intermediate videos...")

    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(temp_folder)


    # -------------------------------------------------
    # Find all lesson folders
    # -------------------------------------------------

    lesson_folders = []

    for root, folders, files in os.walk(temp_folder):

        folder_name = os.path.basename(root)

        match = re.search(
            r"lesson\s*(\d+)",
            folder_name,
            re.IGNORECASE
        )

        if match:
            lesson_number = int(match.group(1))

            if 1 <= lesson_number <= 24:
                lesson_folders.append(
                    (lesson_number, root, folder_name)
                )


    # -------------------------------------------------
    # Sort Lesson 1 → Lesson 24
    # -------------------------------------------------

    lesson_folders.sort(key=lambda x: x[0])


    imported = 0


    # -------------------------------------------------
    # Import each lesson
    # -------------------------------------------------

    for lesson_number, lesson_folder, folder_name in lesson_folders:

        video_files = []

        for filename in os.listdir(lesson_folder):

            if filename.lower().endswith(
                (".mp4", ".mov", ".avi", ".mkv", ".webm")
            ):
                video_files.append(filename)


        # No video found
        if not video_files:
            print(
                f"WARNING: No video found for Lesson {lesson_number}"
            )
            continue


        # More than one video found
        if len(video_files) > 1:
            print(
                f"WARNING: Multiple videos found for Lesson {lesson_number}:"
            )

            for video in video_files:
                print("   ", video)

            print("Skipping this lesson to avoid wrong assignment.")
            continue


        filename = video_files[0]

        video_path = os.path.join(
            lesson_folder,
            filename
        )


        # -------------------------------------------------
        # Create clean title from folder name
        # -------------------------------------------------

        title = re.sub(
            r"lesson\s*\d+",
            "",
            folder_name,
            flags=re.IGNORECASE
        )

        title = re.sub(
            r"\bintermediate\b",
            "",
            title,
            flags=re.IGNORECASE
        )

        title = re.sub(
            r"\ba\.?v\.?\b",
            "",
            title,
            flags=re.IGNORECASE
        )

        title = re.sub(
            r"\s+",
            " ",
            title
        ).strip()

        title = title.title()


        # -------------------------------------------------
        # Get or create Lesson
        # -------------------------------------------------

        lesson, created = Lesson.objects.get_or_create(
            level="Intermediate",
            lesson_number=lesson_number,
            defaults={
                "title": title
            }
        )


        # Keep existing title if already present
        if not lesson.title:
            lesson.title = title
            lesson.save()


        # -------------------------------------------------
        # Get or create VideoLesson
        # -------------------------------------------------

        try:
            video_lesson = lesson.video_lesson

        except VideoLesson.DoesNotExist:
            video_lesson = VideoLesson(
                lesson=lesson
            )


        # Remove old video if present
        if video_lesson.video:
            video_lesson.video.delete(save=False)


        # -------------------------------------------------
        # Save new video
        # -------------------------------------------------

        with open(video_path, "rb") as video_file:

            video_lesson.video.save(
                os.path.basename(filename),
                File(video_file),
                save=True
            )


        imported += 1

        print(
            f"Imported: Intermediate - Lesson {lesson_number} - {title}"
        )


# -------------------------------------------------
# Final result
# -------------------------------------------------

print()
print("===================================")
print(f"SUCCESS! {imported} videos imported.")
print("===================================")