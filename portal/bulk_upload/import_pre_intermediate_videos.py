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

ZIP_FILE = r"D:\pre intermediate lessons a.v.zip"


# -------------------------------------------------
# Check ZIP
# -------------------------------------------------

if not os.path.exists(ZIP_FILE):
    print("ERROR: ZIP file not found:")
    print(ZIP_FILE)
    sys.exit()


# -------------------------------------------------
# Extract and import videos
# -------------------------------------------------

with tempfile.TemporaryDirectory() as temp_folder:

    print("Extracting Pre-Intermediate videos...")

    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(temp_folder)

    imported = 0

    for root, folders, files in os.walk(temp_folder):

        for filename in files:

            if not filename.lower().endswith(
                (".mp4", ".mov", ".avi", ".mkv", ".webm")
            ):
                continue

            video_path = os.path.join(root, filename)

            folder_name = os.path.basename(root)

            # Recognize "lesson" and typo "leesson"
            search_text = folder_name + " " + filename

            match = re.search(
                r"le{1,2}sson\s*(\d+)",
                search_text,
                re.IGNORECASE
            )

            if not match:
                print("Could not find lesson number:", filename)
                continue

            lesson_number = int(match.group(1))

            # Only Lessons 1–24
            if lesson_number < 1 or lesson_number > 24:
                print("Skipping invalid lesson:", filename)
                continue

            # Get existing Lesson or create it
            lesson, created = Lesson.objects.get_or_create(
                level="Pre-Intermediate",
                lesson_number=lesson_number,
                defaults={
                    "title": ""
                }
            )

            # Get existing video or create one
            try:
                video_lesson = lesson.video_lesson
            except VideoLesson.DoesNotExist:
                video_lesson = VideoLesson(
                    lesson=lesson
                )

            # Remove old video if present
            if video_lesson.video:
                video_lesson.video.delete(save=False)

            # Save new video
            with open(video_path, "rb") as video_file:

                video_lesson.video.save(
                    os.path.basename(filename),
                    File(video_file),
                    save=True
                )

            imported += 1

            print(
                f"Imported: Pre-Intermediate - Lesson {lesson_number}"
            )


print()
print("===================================")
print(f"SUCCESS! {imported} videos imported.")
print("===================================")