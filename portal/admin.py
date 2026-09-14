from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.utils import timezone
import urllib.parse
import uuid
import datetime

from .models import Student, Lesson, VideoLesson, StudentLesson, FeeVoucher, Certificate


# =================================================
# AUTOMATIC VOUCHER ENGINE
# =================================================

def run_auto_voucher_generation():
    today = timezone.now().date()
    current_month_str = today.strftime("%B %Y")

    for student in Student.objects.all():
        if student.monthly_fee <= 0:
            continue

        target_day = min(max(student.fee_due_day, 1), 28)

        # Triggers once current date reaches or passes the monthly due day
        if today.day >= target_day:
            already_exists = FeeVoucher.objects.filter(
                student=student,
                billing_month=current_month_str
            ).exists()

            if not already_exists:
                due_date = datetime.date(today.year, today.month, target_day)
                voucher_code = f"SSC-{today.strftime('%y%m')}-{uuid.uuid4().hex[:5].upper()}"

                FeeVoucher.objects.create(
                    student=student,
                    voucher_no=voucher_code,
                    billing_month=current_month_str,
                    amount=student.monthly_fee,
                    due_date=due_date,
                    status="Unpaid"
                )


# =================================================
# FILE UPLOAD WIDGET
# =================================================

class ClearableFileInputWithRemove(forms.ClearableFileInput):
    template_name = "admin/widgets/clearable_file_input.html"


# =================================================
# LESSON FORM
# =================================================

class LessonAdminForm(forms.ModelForm):

    class Meta:
        model = Lesson
        fields = "__all__"
        widgets = {
            "pdf": ClearableFileInputWithRemove(
                attrs={"accept": "application/pdf"}
            ),
        }


# =================================================
# VIDEO LESSON FORM
# =================================================

class VideoLessonAdminForm(forms.ModelForm):

    class Meta:
        model = VideoLesson
        fields = "__all__"
        widgets = {
            "video": ClearableFileInputWithRemove(
                attrs={"accept": "video/*"}
            ),
        }


# =================================================
# STUDENT FORM
# =================================================

class StudentAdminForm(forms.ModelForm):

    beginner_lessons = forms.ModelMultipleChoiceField(
        label="Beginner",
        queryset=Lesson.objects.filter(level="Beginner").order_by("lesson_number"),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    pre_intermediate_lessons = forms.ModelMultipleChoiceField(
        label="Pre-Intermediate",
        queryset=Lesson.objects.filter(level="Pre-Intermediate").order_by("lesson_number"),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    intermediate_lessons = forms.ModelMultipleChoiceField(
        label="Intermediate",
        queryset=Lesson.objects.filter(level="Intermediate").order_by("lesson_number"),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Student
        fields = (
            "name",
            "whatsapp",
            "username",
            "password",
            "monthly_fee",
            "fee_due_day",
            "admission_date",
            "beginner_lessons",
            "pre_intermediate_lessons",
            "intermediate_lessons",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            assigned_lessons = Lesson.objects.filter(
                assigned_students__student=self.instance
            )

            self.fields["beginner_lessons"].initial = assigned_lessons.filter(level="Beginner")
            self.fields["pre_intermediate_lessons"].initial = assigned_lessons.filter(level="Pre-Intermediate")
            self.fields["intermediate_lessons"].initial = assigned_lessons.filter(level="Intermediate")

    def save(self, commit=True):
        student = super().save(commit=commit)

        if student.pk:
            selected_lessons = list(self.cleaned_data.get("beginner_lessons", []))
            selected_lessons += list(self.cleaned_data.get("pre_intermediate_lessons", []))
            selected_lessons += list(self.cleaned_data.get("intermediate_lessons", []))

            StudentLesson.objects.filter(student=student).delete()

            StudentLesson.objects.bulk_create(
                [
                    StudentLesson(student=student, lesson=lesson)
                    for lesson in selected_lessons
                ]
            )

        return student


# =================================================
# STUDENTS ADMIN
# =================================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    form = StudentAdminForm

    list_display = (
        "name",
        "whatsapp",
        "username",
        "monthly_fee",
        "fee_due_day",
        "admission_date",
    )

    search_fields = (
        "name",
        "whatsapp",
        "username",
    )

    actions = ["generate_monthly_vouchers_action"]

    def changelist_view(self, request, extra_context=None):
        run_auto_voucher_generation()
        return super().changelist_view(request, extra_context=extra_context)

    @admin.action(description="Force generate this month's voucher for selected students")
    def generate_monthly_vouchers_action(self, request, queryset):
        today = timezone.now().date()
        current_month = today.strftime("%B %Y")
        created_count = 0

        for student in queryset:
            if not FeeVoucher.objects.filter(student=student, billing_month=current_month).exists():
                target_day = min(max(student.fee_due_day, 1), 28)
                due_date = datetime.date(today.year, today.month, target_day)

                voucher_code = f"SSC-{today.strftime('%y%m')}-{uuid.uuid4().hex[:5].upper()}"

                FeeVoucher.objects.create(
                    student=student,
                    voucher_no=voucher_code,
                    billing_month=current_month,
                    amount=student.monthly_fee,
                    due_date=due_date,
                    status="Unpaid"
                )
                created_count += 1

        self.message_user(request, f"Generated {created_count} voucher(s) for {current_month}.")


# =================================================
# FEE VOUCHERS ADMIN
# =================================================

@admin.register(FeeVoucher)
class FeeVoucherAdmin(admin.ModelAdmin):

    list_display = (
        "voucher_no",
        "student",
        "billing_month",
        "amount",
        "due_date",
        "status",
        "whatsapp_button",
    )

    list_filter = (
        "status",
        "billing_month",
    )

    search_fields = (
        "voucher_no",
        "student__name",
        "student__whatsapp",
    )

    list_editable = ("status",)

    def changelist_view(self, request, extra_context=None):
        run_auto_voucher_generation()
        return super().changelist_view(request, extra_context=extra_context)

    def whatsapp_button(self, obj):
        msg = (
            f"Hello {obj.student.name}!\n\n"
            f"This is a fee reminder from *Shiza Spoken Club*.\n"
            f"• Voucher No: *{obj.voucher_no}*\n"
            f"• Month: *{obj.billing_month}*\n"
            f"• Amount Due: *PKR {obj.amount}*\n"
            f"• Due Date: *{obj.due_date.strftime('%d-%b-%Y')}*\n"
            f"• Status: *{obj.status}*\n\n"
            f"Please log in to your portal to view and clear your dues. Thank you!"
        )
        encoded_msg = urllib.parse.quote(msg)
        phone = obj.student.whatsapp.replace("+", "").replace("-", "").replace(" ", "")
        wa_url = f"https://wa.me/{phone}?text={encoded_msg}"

        return format_html(
            '<a class="button" style="background:#25D366; color:#ffffff; font-weight:bold; padding:5px 10px; border-radius:5px; text-decoration:none; display:inline-block;" href="{}" target="_blank">Send WhatsApp</a>',
            wa_url
        )

    whatsapp_button.short_description = "WhatsApp Reminder"


# =================================================
# CERTIFICATES ADMIN
# =================================================

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "level",
        "issued_date",
        "certificate_file",
    )

    list_filter = (
        "level",
    )

    search_fields = (
        "student__name",
        "level",
    )


# =================================================
# LESSONS ADMIN
# =================================================

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    form = LessonAdminForm

    list_display = (
        "level",
        "lesson_number",
        "title",
        "pdf",
    )

    list_filter = (
        "level",
    )

    search_fields = (
        "title",
    )

    ordering = (
        "level",
        "lesson_number",
    )

    class Media:
        js = ("js/file_upload_remove.js",)


# =================================================
# VIDEO LESSONS ADMIN
# =================================================

@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):

    form = VideoLessonAdminForm

    list_display = (
        "lesson",
        "video",
    )

    list_filter = (
        "lesson__level",
    )

    search_fields = (
        "lesson__title",
    )

    ordering = (
        "lesson__level",
        "lesson__lesson_number",
    )

    class Media:
        js = ("js/file_upload_remove.js",)