"""Views package — re-exports all views for URL routing."""

from .auth import home, log, logOut
from .committee import committee, createCom, viewCom, viewSem, addRole, createSem, assign_acting_chairman, remove_acting_chairman
from .course import (
    createCourse, viewCourse, updateCourse, deleteCourse,
    addInvigilator, indCourse, thesis, supervising,
)
from .billing import examBill, indBill, pdf_view, examBill2, semBill, indBill2, all_bills
from .registration import register, pending_registrations, approve_registration, reject_registration, add_teacher_direct
from .course_code import manage_course_codes, edit_course_code, sync_course_name, course_code_api
from .moderator import manage_moderators, edit_moderator, remove_moderator

__all__ = [
    'home', 'log', 'logOut',
    'committee', 'createCom', 'viewCom', 'viewSem', 'addRole', 'createSem', 'assign_acting_chairman', 'remove_acting_chairman',
    'createCourse', 'viewCourse', 'updateCourse', 'deleteCourse',
    'addInvigilator', 'indCourse', 'thesis', 'supervising',
    'examBill', 'indBill', 'pdf_view', 'examBill2', 'semBill', 'indBill2', 'all_bills',
    'manage_moderators', 'edit_moderator', 'remove_moderator',
]
