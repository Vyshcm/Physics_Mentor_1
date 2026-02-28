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
    path('teacher/assignments/', views.teacher_assignments_view, name='teacher_assignments'),
    path('teacher/quizzes/', views.teacher_quizzes_view, name='teacher_quizzes'),
    path('teacher/exams/', views.teacher_exams_view, name='teacher_exams'),
    path('teacher/payments/', views.teacher_payments_view, name='teacher_payments'),
    path('teacher/doubts/', views.teacher_doubts_view, name='teacher_doubts'),
    path('teacher/parent-messages/', views.teacher_parent_messages_view, name='teacher_parent_messages'),
    path('teacher/student/<int:student_id>/performance/', views.student_performance_view, name='student_performance'),
]
