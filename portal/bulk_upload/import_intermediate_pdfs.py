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

ZIP_FILE = r"D:\Intermediate_Lessons_PDF.zip"


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

    print("Extracting Intermediate PDFs...")

    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(temp_folder)

    pdf_lessons = []

    # Find every PDF
    for root, folders, files in os.walk(temp_folder):

        for filename in files:

            if not filename.lower().endswith(".pdf"):
                continue

            # Supports:
            # Lesson 1.pdf
            # Lesson_01.pdf
            # Lesson-01.pdf
            match = re.search(
                r"lesson[\s_-]*(\d+)",
                filename,
                re.IGNORECASE
            )

            if not match:
                print("Could not find lesson number:", filename)
                continue

            lesson_number = int(match.group(1))

            if 1 <= lesson_number <= 24:

                pdf_lessons.append(
                    (
                        lesson_number,
                        os.path.join(root, filename),
                        filename
                    )
                )


    # -------------------------------------------------
    # Sort Lesson 1 → Lesson 24
    # -------------------------------------------------

    pdf_lessons.sort(key=lambda x: x[0])


    # -------------------------------------------------
    # Import PDFs
    # -------------------------------------------------

    imported = 0

    for lesson_number, pdf_path, filename in pdf_lessons:

        # Get existing Intermediate Lesson
        lesson, created = Lesson.objects.get_or_create(
            level="Intermediate",
            lesson_number=lesson_number,
            defaults={
                "title": ""
            }
        )


        # Remove existing PDF if present
        if lesson.pdf:
            lesson.pdf.delete(save=False)


        # Save new PDF
        with open(pdf_path, "rb") as pdf_file:

            lesson.pdf.save(
                os.path.basename(filename),
                File(pdf_file),
                save=True
            )


        imported += 1

        print(
            f"Imported: Intermediate - Lesson {lesson_number}"
        )


# -------------------------------------------------
# Final result
# -------------------------------------------------

print()
print("===================================")
print(f"SUCCESS! {imported} PDFs imported.")
print("===================================")