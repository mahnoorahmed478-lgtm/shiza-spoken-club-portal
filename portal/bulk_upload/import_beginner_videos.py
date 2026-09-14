import os
import re
import sys
import zipfile
import tempfile
import shutil

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


from django.conf import settings
from django.core.files import File

from portal.models import Lesson, VideoLesson


# -------------------------------------------------
# ZIP file location
# -------------------------------------------------

ZIP_FILE = r"D:\Beginner Video Lessons.zip"


# -------------------------------------------------
# Extract and import videos
# -------------------------------------------------

if not os.path.exists(ZIP_FILE):
    print("ERROR: ZIP file not found:")
    print(ZIP_FILE)
    sys.exit()


with tempfile.TemporaryDirectory() as temp_folder:

    print("Extracting videos...")

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

            # Get the folder containing the video
            folder_name = os.path.basename(root)

            # Find lesson number
            match = re.search(
                r"lesson\s*(\d+)",
                folder_name,
                re.IGNORECASE
            )

            if not match:
                print("Could not find lesson number:", folder_name)
                continue

            lesson_number = int(match.group(1))

            # Get title from folder name
            title = re.sub(
                r"lesson\s*\d+",
                "",
                folder_name,
                flags=re.IGNORECASE
            )

            # Remove common extra words
            title = re.sub(
                r"\bbeginner\b",
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

            # Remove brackets
            title = re.sub(r"\([^)]*\)", "", title)

            # Clean spaces
            title = re.sub(r"\s+", " ", title).strip()

            # Correct known typo
            if lesson_number == 24:
                title = "Feelings"

            # Create or update Lesson
            lesson, created = Lesson.objects.get_or_create(
                level="Beginner",
                lesson_number=lesson_number,
                defaults={
                    "title": title
                }
            )

            # Update title if necessary
            if lesson.title != title:
                lesson.title = title
                lesson.save()

            # Create or update VideoLesson
            video_lesson, created_video = VideoLesson.objects.get_or_create(
                lesson=lesson
            )

            # Remove old video if one already exists
            if video_lesson.video:
                old_video_path = video_lesson.video.path

                if os.path.exists(old_video_path):
                    os.remove(old_video_path)

                video_lesson.video = None

            # Save new video
            with open(video_path, "rb") as video_file:

                video_lesson.video.save(
                    filename,
                    File(video_file),
                    save=True
                )

            imported += 1

            print(
                f"Imported: Beginner - Lesson {lesson_number} - {title}"
            )


print()
print("===================================")
print(f"SUCCESS! {imported} videos imported.")
print("===================================")