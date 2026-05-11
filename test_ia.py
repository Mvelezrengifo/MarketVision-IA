import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def probar_gemini_2_5():
    print("🚀 Probando conexión con el nuevo Gemini 2.5 Flash...")

    # Usamos el nombre exacto que nos dio tu lista
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={api_key}"

    headers = {'Content-Type': 'application/json'}

    data = {
        "contents": [{
            "parts": [{"text": "Hola, soy Mauro, tu desarrollador. Estamos montando MarketVision para analizar criptos y acciones. ¡Dame un saludo de bienvenida al equipo"}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print("✅ ¡CONEXIÓN EXITOSA!")
            res_json = response.json()
            texto = res_json['candidates'][0]['content']['parts'][0]['text']
            print("\nGemini 2.5 dice:", texto)
        else:
            print(f"❌ Error {response.status_code}: {response.text}")

    except Exception as e:
        print(f"💥 Error inesperado: {e}")


if __name__ == "__main__":
    probar_gemini_2_5()