"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from portal.views import (
    home,
    student_login,
    student_dashboard,
    my_lessons,
    my_account,
    student_fees,
    view_voucher,
    student_certificates,
    student_logout,
)


urlpatterns = [

    path(
        "admin/",
        admin.site.urls
    ),

    path(
        "",
        home,
        name="home"
    ),

    path(
        "login/",
        student_login,
        name="student_login"
    ),

    path(
        "dashboard/",
        student_dashboard,
        name="student_dashboard"
    ),

    path(
        "lessons/",
        my_lessons,
        name="my_lessons"
    ),

    path(
        "my-account/",
        my_account,
        name="my_account"
    ),

    path(
        "fees/",
        student_fees,
        name="student_fees"
    ),

    path(
        "voucher/<int:voucher_id>/",
        view_voucher,
        name="view_voucher"
    ),

    path(
        "certificates/",
        student_certificates,
        name="student_certificates"
    ),

    path(
        "logout/",
        student_logout,
        name="student_logout"
    ),
]


# Serve uploaded PDFs, videos, and certificates during development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )