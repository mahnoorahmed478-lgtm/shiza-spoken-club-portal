from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Student, StudentLesson, FeeVoucher, Certificate


def home(request):
    return render(request, "home.html")


# =========================
# STUDENT LOGIN
# =========================

def student_login(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        try:

            student = Student.objects.get(
                username__iexact=username
            )

            if student.password == password:

                request.session["student_id"] = student.id

                return redirect("student_dashboard")

            else:

                messages.error(
                    request,
                    "Incorrect password."
                )

        except Student.DoesNotExist:

            messages.error(
                request,
                "Username not found."
            )

    return render(request, "login.html")


# =========================
# GET LOGGED-IN STUDENT
# =========================

def get_logged_in_student(request):

    student_id = request.session.get("student_id")

    if not student_id:
        return None

    try:

        return Student.objects.get(
            id=student_id
        )

    except Student.DoesNotExist:

        request.session.flush()

        return None


# =========================
# DASHBOARD
# =========================

def student_dashboard(request):

    student = get_logged_in_student(request)

    if not student:
        return redirect("student_login")

    return render(
        request,
        "student_dashboard.html",
        {
            "student": student
        }
    )


# =========================
# MY LESSONS
# =========================

def my_lessons(request):

    student = get_logged_in_student(request)

    if not student:
        return redirect("student_login")

    assigned_lessons = (
        StudentLesson.objects
        .filter(
            student=student
        )
        .select_related(
            "lesson"
        )
        .prefetch_related(
            "lesson__video_lesson"
        )
        .order_by(
            "lesson__lesson_number"
        )
    )

    return render(
        request,
        "my_lessons.html",
        {
            "student": student,
            "assigned_lessons": assigned_lessons,
        }
    )


# =========================
# MY ACCOUNT
# =========================

def my_account(request):

    student = get_logged_in_student(request)

    if not student:
        return redirect("student_login")

    return render(
        request,
        "my_account.html",
        {
            "student": student
        }
    )


# =========================
# FEES PORTAL (NEW)
# =========================

def student_fees(request):

    student = get_logged_in_student(request)

    if not student:
        return redirect("student_login")

    vouchers = FeeVoucher.objects.filter(student=student).order_by("-id")

    return render(
        request,
        "fees.html",
        {
            "student": student,
            "vouchers": vouchers,
        }
    )


# =========================
# VIEW / PRINT VOUCHER (NEW)
# =========================

def view_voucher(request, voucher_id):

    student = get_logged_in_student(request)

    # Permit logged-in student or an authenticated admin to view
    if not student and not request.user.is_staff:
        return redirect("student_login")

    if student:
        voucher = get_object_or_404(FeeVoucher, id=voucher_id, student=student)
    else:
        voucher = get_object_or_404(FeeVoucher, id=voucher_id)

    return render(
        request,
        "voucher_print.html",
        {
            "voucher": voucher,
            "student": voucher.student,
        }
    )


# =========================
# CERTIFICATES PORTAL (NEW)
# =========================

def student_certificates(request):

    student = get_logged_in_student(request)

    if not student:
        return redirect("student_login")

    certificates = Certificate.objects.filter(student=student).order_by("-issued_date")

    return render(
        request,
        "certificates.html",
        {
            "student": student,
            "certificates": certificates,
        }
    )


# =========================
# LOGOUT
# =========================

def student_logout(request):

    request.session.flush()

    return redirect("student_login")