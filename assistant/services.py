# services.py
import re
import requests
from django.conf import settings
from hp_management.models import Appointment, Doctor, About, Services


def get_ai_response(message, user=None):
    """
    AI-powered hospital assistant:
    - Fetches data from database
    - Sends it to AI to generate human-like responses
    """
    try:
        msg = (message or "").lower()

        # Helper to normalize text
        def normalize(text):
            if not text:
                return ""
            return re.sub(r"[^a-z0-9]", "", text.lower())

        norm_msg = normalize(msg)

        # Prepare context for AI
        ai_context = {
            "appointments": [],
            "doctors": [],
            "abouts": [],
            "services": [],
        }

        # 1️⃣ Appointments
        if user and getattr(user, "is_authenticated", False):
            appointments = Appointment.objects.filter(user=user).order_by("-date")
            for appt in appointments:
                ai_context["appointments"].append(
                    {
                        "doctor": appt.doctor.name if appt.doctor else "Not Assigned",
                        "date": str(appt.date),
                        "time": str(appt.time),
                        "status": appt.appointment_status,
                    }
                )

        # 2️⃣ Doctors
        doctors = Doctor.objects.filter(is_active=True)
        for doc in doctors:
            ai_context["doctors"].append(
                {
                    "name": doc.name,
                    "specialization": doc.specialization,
                    "phone": doc.phone,
                    "email": doc.email,
                }
            )

        # 3️⃣ About us
        abouts = About.objects.all()
        for a in abouts:
            ai_context["abouts"].append(a.about_text)

        # 4️⃣ Services
        services = Services.objects.all()
        for s in services:
            ai_context["services"].append(
                {"name": s.service_name, "description": s.service_description}
            )

        # 5️⃣ Send message + data context to AI
        system_prompt = (
            "You are a friendly hospital assistant named Lina. "
            "Answer naturally and warmly. "
            "Use the provided data to respond where possible. "
            "Do not say you are a computer or AI. "
            "Keep answers concise and encouraging."
        )

        response_payload = {
            "model": "openrouter/auto",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
                {
                    "role": "user",
                    "content": f"Here is the hospital data you can use:\n{ai_context}",
                },
            ],
            "max_tokens": 200,
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=response_payload,
                timeout=10,
            )
            data = response.json()
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print("AI ERROR:", e)
            return "Sorry, I couldn't answer that just now. Please try again."

        return "I'm not sure about that. You can ask about appointments, doctors, hospital info, about us, or services."

    except Exception as e:
        print("Assistant ERROR:", e)
        return "Something went wrong. Please try again."
