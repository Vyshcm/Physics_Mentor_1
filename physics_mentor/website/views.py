from django.shortcuts import render,redirect
from django.conf import settings
import requests
from django.http import JsonResponse
import json
import time
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

def ai_doubt_solver(request):
    return render(request, "ai_doubt_solver.html")

def ai_chat(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "").strip()
            
            if not user_message:
                return JsonResponse({"error": "Message is required"}, status=400)
                
            api_key = getattr(settings, 'DEEPSEEK_API_KEY', None)
            if not api_key or api_key in ['YOUR_DEEPSEEK_API_KEY_HERE', 'your_real_key_here', 'your_actual_api_key_here']:
                return JsonResponse({"error": "DeepSeek API key is missing. Please add it to your .env file and restart the server."}, status=500)
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful Physics Mentor AI for students. Explain clearly and simply. Provide step-by-step explanation when needed. Keep responses concise."},
                    {"role": "user", "content": user_message}
                ],
                "stream": False
            }
            
            response = requests.post(
                "https://api.deepseek.com/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                return JsonResponse({"error": f"DeepSeek API error: {response.status_code} {response.text}"}, status=500)
                
            response_data = response.json()
            ai_reply = response_data['choices'][0]['message']['content']
            
            return JsonResponse({"reply": ai_reply})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=405)
