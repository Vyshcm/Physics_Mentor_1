from django.urls import path
# from .views import home
from . import views

urlpatterns = [
    path('signup/',views.signup,name='signup'),
    path('login/',views.Login,name='login'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('logout/',views.logout,name='logout'),
    path('forgotpassword/',views.forgotpassword,name='forgotpassword'),
    path('payment/',views.payment,name='payment'),
    path('payment/success/',views.payment_success,name='payment_success'),
    path('feedback/',views.feedback_view,name='feedback'),
    path('doubt-sessions/',views.doubt_sessions_view,name='doubt_sessions'),
    path('parent/dashboard/',views.parent_dashboard_view,name='parent_dashboard'),

    # Teacher Dashboard URLs
    path('teacher/dashboard/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('teacher/students/', views.teacher_students_view, name='teacher_students'),
    path('teacher/attendance/', views.teacher_attendance_view, name='teacher_attendance'),
    path('teacher/attendance/history/', views.teacher_attendance_history_view, name='teacher_attendance_history'),
    path('teacher/attendance/student/', views.teacher_student_attendance_report_view, name='teacher_student_attendance_report'),
    path('teacher/attendance/student/<int:student_id>/', views.teacher_student_attendance_report_view, name='teacher_student_attendance_report_detail'),
    path('teacher/assignments/', views.teacher_assignments_view, name='teacher_assignments'),
    path('teacher/quizzes/', views.teacher_quizzes_view, name='teacher_quizzes'),
    path('teacher/quizzes/<int:quiz_id>/questions/', views.teacher_quiz_questions_view, name='teacher_quiz_questions'),
    path('teacher/quizzes/<int:quiz_id>/toggle-publish/', views.teacher_quiz_toggle_publish, name='teacher_quiz_toggle_publish'),
    path('teacher/exams/', views.teacher_exams_view, name='teacher_exams'),
    path('teacher/exams/<int:exam_id>/submissions/', views.teacher_exam_submissions, name='teacher_exam_submissions'),
    path('teacher/exams/submission/<int:submission_id>/grade/', views.grade_exam_submission, name='grade_exam_submission'),
    path('teacher/payments/', views.teacher_payments_view, name='teacher_payments'),
    path('teacher/doubts/', views.teacher_doubts_view, name='teacher_doubts'),
    path('teacher/parent-messages/', views.teacher_parent_messages_view, name='teacher_parent_messages'),
    path('teacher/student/<int:student_id>/performance/', views.student_performance_view, name='student_performance'),
    path('teacher/notes/', views.teacher_notes_view, name='teacher_notes'),
    path('teacher/notes/<int:note_id>/edit/', views.teacher_note_edit_view, name='teacher_note_edit'),
    path('teacher/notes/<int:note_id>/delete/', views.teacher_note_delete_view, name='teacher_note_delete'),
    path('teacher/live-classes/', views.teacher_live_classes_view, name='teacher_live_classes'),
    path('teacher/assignments/<int:assignment_id>/submissions/', views.teacher_assignment_submissions, name='teacher_assignment_submissions'),

    # Student Assignment URLs
    path('student/assignments/', views.student_assignments_view, name='student_assignments'),
    path('student/assignments/<int:assignment_id>/', views.student_assignment_detail_view, name='student_assignment_detail'),
    path('student/live-classes/', views.student_live_classes, name='student_live_classes'),
    path('student/notes/', views.student_notes, name='student_notes'),
    path('student/attendance/', views.student_attendance, name='student_attendance'),
    path('student/exams/', views.student_exams, name='student_exams'),
    path('student/exams/<int:exam_id>/upload/', views.upload_exam_submission, name='upload_exam_submission'),
    # Student Quiz URLs
    path('student/quizzes/', views.student_quizzes, name='student_quizzes'),
    path('student/quizzes/<int:quiz_id>/', views.student_quiz_instructions, name='student_quiz_instructions'),
    path('student/quizzes/<int:quiz_id>/start/', views.student_quiz_start, name='student_quiz_start'),
    path('student/quizzes/<int:quiz_id>/submit/', views.student_quiz_submit, name='student_quiz_submit'),
    path('student/quizzes/<int:quiz_id>/result/', views.student_quiz_result, name='student_quiz_result'),
    path('student/progress/', views.student_progress, name='student_progress'),
]
