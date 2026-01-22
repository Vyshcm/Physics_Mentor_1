from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'website/home.html')

def about(request):
    return render(request, "website/about.html")

def courses(request):
    return render(request, "website/courses.html")

def features(request):
    return render(request, "website/features.html")

def testimonials(request):
    return render(request, "website/testimonials.html")

def contact(request):
    return render(request, "website/contact.html")
