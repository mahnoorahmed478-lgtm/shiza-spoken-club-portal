from django.db import models
from django.utils import timezone


# =========================
# STUDENTS
# =========================

class Student(models.Model):

    name = models.CharField(
        max_length=100
    )

    whatsapp = models.CharField(
        max_length=20
    )

    username = models.CharField(
        max_length=100,
        unique=True
    )

    password = models.CharField(
        max_length=100
    )

    monthly_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Standard monthly fee for this student"
    )

    admission_date = models.DateField(
        default=timezone.now,
        help_text="Date of admission"
    )

    fee_due_day = models.PositiveSmallIntegerField(
        default=5,
        help_text="Day of the month the voucher is generated and due (1 to 28)"
    )

    def __str__(self):
        return self.name


# =========================
# LESSONS
# =========================

class Lesson(models.Model):

    LEVEL_CHOICES = [
        ("Beginner", "Beginner"),
        ("Pre-Intermediate", "Pre-Intermediate"),
        ("Intermediate", "Intermediate"),
    ]

    level = models.CharField(
        max_length=30,
        choices=LEVEL_CHOICES
    )

    lesson_number = models.PositiveIntegerField()

    title = models.CharField(
        max_length=200,
        blank=True
    )

    pdf = models.FileField(
        upload_to="lessons/pdfs/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.level} - Lesson {self.lesson_number}"

    class Meta:
        ordering = [
            "level",
            "lesson_number"
        ]

        unique_together = [
            "level",
            "lesson_number"
        ]


# =========================
# VIDEO LESSON
# =========================

class VideoLesson(models.Model):

    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name="video_lesson"
    )

    video = models.FileField(
        upload_to="lessons/videos/"
    )

    def __str__(self):
        return f"{self.lesson} - Video"


# =========================
# STUDENT LESSON ASSIGNMENT
# =========================

class StudentLesson(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="assigned_lessons"
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="assigned_students"
    )

    assigned_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.student.name} → {self.lesson}"

    class Meta:
        unique_together = [
            "student",
            "lesson"
        ]


# =========================
# FEE VOUCHER
# =========================

class FeeVoucher(models.Model):

    STATUS_CHOICES = [
        ("Unpaid", "Unpaid"),
        ("Paid", "Paid"),
        ("Overdue", "Overdue"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="fee_vouchers"
    )

    voucher_no = models.CharField(
        max_length=50,
        unique=True
    )

    billing_month = models.CharField(
        max_length=30,
        help_text="e.g. September 2026"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    due_date = models.DateField()

    issue_date = models.DateField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Unpaid"
    )

    def __str__(self):
        return f"{self.voucher_no} - {self.student.name} ({self.billing_month})"


# =========================
# CERTIFICATES
# =========================

class Certificate(models.Model):

    LEVEL_CHOICES = [
        ("Beginner", "Beginner"),
        ("Pre-Intermediate", "Pre-Intermediate"),
        ("Intermediate", "Intermediate"),
        ("Course Completion", "Course Completion"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="certificates"
    )

    level = models.CharField(
        max_length=50,
        choices=LEVEL_CHOICES
    )

    certificate_file = models.FileField(
        upload_to="certificates/"
    )

    issued_date = models.DateField(
        default=timezone.now
    )

    def __str__(self):
        return f"{self.student.name} - {self.level} Certificate"