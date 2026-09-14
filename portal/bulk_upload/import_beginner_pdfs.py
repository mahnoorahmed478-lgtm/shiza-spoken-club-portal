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
from portal.models import Lesson


# -------------------------------------------------
# ZIP file location
# -------------------------------------------------

ZIP_FILE = r"D:\Beginner_Lessons_PDFs_Compressed.zip"


# -------------------------------------------------
# Check ZIP
# -------------------------------------------------

if not os.path.exists(ZIP_FILE):
    print("ERROR: ZIP file not found:")
    print(ZIP_FILE)
    sys.exit()


# -------------------------------------------------
# Extract and import PDFs
# -------------------------------------------------

with tempfile.TemporaryDirectory() as temp_folder:

    print("Extracting PDFs...")

    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(temp_folder)

    imported = 0

    for root, folders, files in os.walk(temp_folder):

        for filename in files:

            if not filename.lower().endswith(".pdf"):
                continue

            pdf_path = os.path.join(root, filename)

            # Find lesson number from filename
            match = re.search(
                r"lesson\s*(\d+)",
                filename,
                re.IGNORECASE
            )

            if not match:
                print("Could not find lesson number:", filename)
                continue

            lesson_number = int(match.group(1))

            # Only Beginner Lessons 1–24
            if lesson_number < 1 or lesson_number > 24:
                print("Skipping invalid lesson:", filename)
                continue

            # Find existing Lesson
            lesson, created = Lesson.objects.get_or_create(
                level="Beginner",
                lesson_number=lesson_number,
                defaults={
                    "title": ""
                }
            )

            # Remove old PDF if one already exists
            if lesson.pdf:
                lesson.pdf.delete(save=False)

            # Upload new PDF
            with open(pdf_path, "rb") as pdf_file:

                lesson.pdf.save(
                    os.path.basename(filename),
                    File(pdf_file),
                    save=True
                )

            imported += 1

            print(
                f"Imported: Beginner - Lesson {lesson_number} - {filename}"
            )


print()
print("===================================")
print(f"SUCCESS! {imported} PDFs imported.")
print("===================================")