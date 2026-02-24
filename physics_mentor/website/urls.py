from django.urls import path
# from .views import home
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("about/", views.about, name="about"),
    path("courses/", views.courses, name="courses"),
    path("features/", views.features, name="features"),
    path("testimonials/", views.testimonials, name="testimonials"),
    path("contact/", views.contact, name="contact"),
     path("aboutus/", views.aboutus, name="aboutus"),
     path('ai-doubt-solver/', views.ai_doubt_solver, name='ai_doubt_solver'),
     path('ai-chat/', views.ai_chat, name='ai_chat'),
]
