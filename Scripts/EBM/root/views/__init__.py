"""Views package — re-exports all views for URL routing."""

from .auth import home, log, logOut
from .committee import committee, createCom, viewCom, viewSem, addRole, createSem
from .course import (
    createCourse, viewCourse, updateCourse, deleteCourse,
    addInvigilator, indCourse, thesis, supervising,
)
from .billing import examBill, indBill, pdf_view, examBill2, semBill, indBill2

__all__ = [
    'home', 'log', 'logOut',
    'committee', 'createCom', 'viewCom', 'viewSem', 'addRole', 'createSem',
    'createCourse', 'viewCourse', 'updateCourse', 'deleteCourse',
    'addInvigilator', 'indCourse', 'thesis', 'supervising',
    'examBill', 'indBill', 'pdf_view', 'examBill2', 'semBill', 'indBill2',
]
