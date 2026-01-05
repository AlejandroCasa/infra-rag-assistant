import os

import google.generativeai as genai
from dotenv import load_dotenv

# Cargar API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: No se encontró la GOOGLE_API_KEY en el archivo .env")
    exit()

# Configurar SDK
genai.configure(api_key=api_key)

print("🔍 Conectando con Google AI para ver tus modelos disponibles...")
print("-------------------------------------------------------------")

try:
    found = False
    for m in genai.list_models():
        # Filtramos solo los modelos que sirven para chatear (generateContent)
        if "generateContent" in m.supported_generation_methods:
            print(f"✅ Disponible: {m.name}")
            found = True

    if not found:
        print("⚠️ No se encontraron modelos compatibles con 'generateContent'.")

except Exception as e:
    print(f"❌ Error de conexión: {e}")
