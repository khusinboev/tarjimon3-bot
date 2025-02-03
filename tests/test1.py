import requests

url = "http://localhost:5000/translate"

payload = {
    "q": "Salom dunyo",  # Tarjima qilinishi kerak bo'lgan matn
    "source": "uz",      # Asl til (masalan, uz - o'zbek)
    "target": "en"       # Maqsad til (masalan, en - ingliz)
}

response = requests.post(url, json=payload)
if response.status_code == 200:
    result = response.json()
    print("Tarjima:", result["translatedText"])
else:
    print("Xatolik:", response.text)
