# views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from .services import get_ai_response


def chat_page(request):
    return render(request, "assistant/chat.html")


@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")

        # Pass the logged-in user to the AI function
        reply = get_ai_response(message, user=request.user)

        return JsonResponse({"reply": reply})
