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
]
