from django.shortcuts import render,redirect
from .forms import ContactQueryForm

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

def aboutus(request):
    return render(request, "website/aboutus.html")






def contact(request):
    success = False

    if request.method == "POST":
        form = ContactQueryForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = ContactQueryForm()  # reset form after submit
    else:
        form = ContactQueryForm()

    return render(request, "website/contact.html", {
        "form": form,
        "success": success
    })
