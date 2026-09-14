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
# ZIP file
# -------------------------------------------------

ZIP_FILE = r"D:\Pre_Intermediate_Lessons_PDFs.zip"


# -------------------------------------------------
# Lesson titles
# -------------------------------------------------

LESSON_TITLES = {
    1: "Things People Do",
    2: "Family and Friends",
    3: "Talking About Places",
    4: "On the Move",
    5: "Talking About Now",
    6: "Food and Drink",
    7: "The Past",
    8: "A Place to Live",
    9: "I've Done It",
    10: "Clothes",
    11: "Quantity",
    12: "How Do You Feel?",
    13: "What Will Happen?",
    14: "About Town",
    15: "Comparing Things",
    16: "Free Time",
    17: "Rules and Advice",
    18: "A Day's Work",
    19: "Telling Stories",
    20: "People",
    21: "Future Plans",
    22: "Around the World",
    23: "Past and Present",
    24: "Arts and Entertainment",
}


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

    print("Extracting Pre-Intermediate PDFs...")

    with zipfile.ZipFile(ZIP_FILE, "r") as zip_ref:
        zip_ref.extractall(temp_folder)


    # -------------------------------------------------
    # Find PDFs
    # -------------------------------------------------

    pdf_lessons = []

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

                print(
                    "Could not find lesson number:",
                    filename
                )

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

    pdf_lessons.sort(
        key=lambda x: x[0]
    )


    # -------------------------------------------------
    # Import PDFs + Titles
    # -------------------------------------------------

    imported = 0


    for lesson_number, pdf_path, filename in pdf_lessons:

        title = LESSON_TITLES[lesson_number]


        # Get existing lesson
        lesson, created = Lesson.objects.get_or_create(
            level="Pre-Intermediate",
            lesson_number=lesson_number,
            defaults={
                "title": title
            }
        )


        # -------------------------------------------------
        # Update title
        # -------------------------------------------------

        lesson.title = title


        # -------------------------------------------------
        # Remove old PDF
        # -------------------------------------------------

        if lesson.pdf:

            lesson.pdf.delete(
                save=False
            )


        # -------------------------------------------------
        # Save new PDF
        # -------------------------------------------------

        with open(pdf_path, "rb") as pdf_file:

            lesson.pdf.save(
                os.path.basename(filename),
                File(pdf_file),
                save=False
            )


        lesson.save()


        imported += 1


        print(
            f"Imported: Pre-Intermediate - "
            f"Lesson {lesson_number} - {title}"
        )


# -------------------------------------------------
# Final result
# -------------------------------------------------

print()

print("==============================================")

print(
    f"SUCCESS! {imported} Pre-Intermediate PDFs imported."
)

print("Titles added successfully.")

print("==============================================")