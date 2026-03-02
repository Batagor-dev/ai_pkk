from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import os

# ================= APP SETUP =================
app = Flask(__name__)
CORS(app)

# ================= API CONFIG =================
API_KEY = os.getenv("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")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "arcee-ai/trinity-large-preview:free"

# ================= LOAD SCHOOL DATA =================
with open("bppi.json", "r", encoding="utf-8") as f:
    SCHOOL_DATA = json.load(f)

# ================= SYSTEM PROMPTS =================
BASE_PROMPT = """
Kamu adalah asisten percakapan yang berperilaku seperti manusia.
Jawaban singkat, natural, dan relevan.
Jika informasi dari user belum cukup, AJUKAN 1 pertanyaan klarifikasi.
Jangan melebar ke topik lain.
Jangan menyebut dirimu AI, sistem, atau model.
"""

BPPI_PROMPT = f"""
Kamu adalah konselor pendidikan SMK.
Gunakan HANYA data berikut sebagai referensi fakta:
{json.dumps(SCHOOL_DATA, ensure_ascii=False)}

Aturan wajib:
- Jangan mengarang data di luar JSON
- Jika informasi user belum cukup, tanya balik dulu
- Fokus hanya pada pertanyaan user
- Gunakan bahasa percakapan alami
"""

# ================= AI CORE =================
def chat_with_ai(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 350,
        "temperature": 0.7
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

# ================= HELPER =================
def should_use_bppi(context: dict, message: str) -> bool:
    """
    BPPI hanya aktif jika:
    - user sudah menyatakan ingin rekomendasi sekolah / SMK
    - atau frontend memaksa lewat flag
    """
    keywords = [
        "rekomendasi smk",
        "sekolah smk",
        "jurusan smk",
        "sekolah kejuruan"
    ]

    if context.get("use_bppi") is True:
        return True

    msg = message.lower()
    return any(k in msg for k in keywords)

# ================= CHAT ENDPOINT =================
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json

    user_message = data.get("message", "")
    chat_history = data.get("history", [])
    context = data.get("context", {})  # simpan state chat

    use_bppi = should_use_bppi(context, user_message)

    messages = []

    # Base behavior (human-like)
    messages.append({
        "role": "system",
        "content": BASE_PROMPT
    })

    # BPPI hanya aktif di momen tertentu
    if use_bppi:
        messages.append({
            "role": "system",
            "content": BPPI_PROMPT
        })

    # Masukkan history biar nyambung
    for h in chat_history:
        messages.append(h)

    messages.append({
        "role": "user",
        "content": user_message
    })

    reply = chat_with_ai(messages)

    return jsonify({
        "reply": reply,
        "use_bppi": use_bppi
    })

# ================= STRUCTURED SMK RECOMMENDATION =================
@app.route("/api/recommend/smk", methods=["POST"])
def recommend_smk():
    answers = request.json.get("answers", [])

    messages = [
        {"role": "system", "content": BASE_PROMPT},
        {"role": "system", "content": BPPI_PROMPT}
    ]

    for a in answers:
        messages.append({"role": "user", "content": a})

    messages.append({
        "role": "user",
        "content": (
            "Berdasarkan jawaban di atas, jika informasi belum cukup, "
            "ajukan pertanyaan klarifikasi terlebih dahulu. "
            "Jika sudah cukup, berikan rekomendasi jurusan SMK yang paling cocok "
            "dan sebutkan sekolah dari data jika relevan."
        )
    })

    reply = chat_with_ai(messages)

    return jsonify({"reply": reply})

# ================= SCHOOL DATA =================
@app.route("/api/school", methods=["GET"])
def school():
    return jsonify(SCHOOL_DATA)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
