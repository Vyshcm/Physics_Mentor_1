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
    path('teacher/payments/', views.teacher_payments_view, name='teacher_payments'),
    path('teacher/doubts/', views.teacher_doubts_view, name='teacher_doubts'),
    path('teacher/parent-messages/', views.teacher_parent_messages_view, name='teacher_parent_messages'),
    path('teacher/student/<int:student_id>/performance/', views.student_performance_view, name='student_performance'),
    path('teacher/notes/', views.teacher_notes_view, name='teacher_notes'),
    path('teacher/notes/<int:note_id>/edit/', views.teacher_note_edit_view, name='teacher_note_edit'),
    path('teacher/notes/<int:note_id>/delete/', views.teacher_note_delete_view, name='teacher_note_delete'),
    path('teacher/live-classes/', views.teacher_live_classes_view, name='teacher_live_classes'),
]
