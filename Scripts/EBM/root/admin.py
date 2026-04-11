"""Admin configuration for all EBM models."""

from django.contrib import admin
from .models import (
    faculty, External, Session, Semester,
    SemesterBill, Course, courseBill,
    ThesisPaper, ThesisSupervisor,
)


@admin.register(faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'username', 'title')
    search_fields = ('name', 'email', 'username')
    list_filter = ('title',)


@admin.register(External)
class ExternalAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('year',)
    ordering = ('-year',)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('session', 'semId', 'chairman', 'tabular1', 'tabular2', 'external')
    list_filter = ('session',)
    ordering = ('session', 'semId')


@admin.register(SemesterBill)
class SemesterBillAdmin(admin.ModelAdmin):
    list_display = ('session', 'semester', 'teacher', 'moderator', 'translator', 'typist')
    list_filter = ('session', 'moderator', 'translator', 'typist')
    search_fields = ('teacher__name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('courseName', 'courseCode', 'type', 'session', 'semester', 'internal', 'external')
    list_filter = ('type', 'session')
    search_fields = ('courseName',)


@admin.register(courseBill)
class CourseBillAdmin(admin.ModelAdmin):
    list_display = ('course', 'extra', 'session', 'semester')
    list_filter = ('session',)


@admin.register(ThesisPaper)
class ThesisPaperAdmin(admin.ModelAdmin):
    list_display = ('course', 'faculty', 'paperNo', 'session', 'semester')
    list_filter = ('session',)
    search_fields = ('faculty__name',)


@admin.register(ThesisSupervisor)
class ThesisSupervisorAdmin(admin.ModelAdmin):
    list_display = ('course', 'faculty', 'studentNo', 'session', 'semester')
    list_filter = ('session',)
    search_fields = ('faculty__name',)
