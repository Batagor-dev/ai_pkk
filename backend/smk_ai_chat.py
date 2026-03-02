from dotenv import load_dotenv
import requests
import json
import os
from datetime import datetime
from requests.exceptions import RequestException

# ================= TERMINAL UI =================
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_terminal()

    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

    print(GREEN + "=" * 55 + RESET)
    print(GREEN + "  _  __     _     _   _     _   _   _____ " + RESET)
    print(GREEN + " | |/ /    / \\   | \\ | |   | | | | |_   _|" + RESET)
    print(GREEN + " | ' /    / _ \\  |  \\| |   | | | |   | |  " + RESET)
    print(GREEN + " | . \\   / ___ \\ | |\\  |   | |_| |   | |  " + RESET)
    print(GREEN + " |_|\\_\\ /_/   \\_\\|_| \\_|    \\___/    |_|  " + RESET)
    print(GREEN + "=" * 55 + RESET)

    print(CYAN + "KANUT Terminal AI Engine" + RESET)
    print("Environment : Development")
    print(f"Started at  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(GREEN + "=" * 55 + RESET)
    print()

# ================= API CONFIG =================
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "arcee-ai/trinity-large-preview:free"

# ================= LOAD SCHOOL DATA =================
def load_school_data():
    with open("bppi.json", "r", encoding="utf-8") as f:
        return json.load(f)

SCHOOL_DATA = load_school_data()

# ================= SYSTEM PROMPTS =================
SYSTEM_PROMPTS = {
    "free": (
        "Kamu adalah AI percakapan santai dan informatif. "
        "Jawaban jelas, tidak bertele-tele, dan mudah dipahami."
    ),
    "smk": (
        "Kamu adalah konselor pendidikan khusus jurusan SMK.\n"
        "Gunakan data sekolah berikut sebagai referensi FAKTUAL:\n"
        f"{json.dumps(SCHOOL_DATA, ensure_ascii=False)}\n\n"
        "DILARANG mengarang data di luar JSON."
    ),
    "campus": (
        "Kamu adalah konselor jurusan kuliah.\n"
        "Berikan saran jurusan realistis.\n"
        "Sertakan PTN & PTS relevan beserta nama jurusannya."
    )
}

# ================= QUESTIONS =================
AI_QUESTIONS_SMK = [
    "Apa hobi utama kamu?",
    "Skill apa yang paling kamu kuasai?",
    "Kamu lebih suka praktik atau teori?"
]

AI_QUESTIONS_CAMPUS = [
    "Pelajaran apa yang paling kamu sukai?",
    "Apa yang ingin kamu pelajari lebih dalam?",
    "Lebih suka logika & data atau kreativitas?",
    "Setelah lulus ingin kerja di bidang apa?",
    "Lebih suka riset atau praktik lapangan?"
]

# ================= STATE =================
consultation_done = False
last_mode = None

# ================= MODE DETECTION =================
def detect_mode(user_input):
    global consultation_done

    text = user_input.lower()

    # Jika sudah konsultasi, jangan auto masuk lagi
    if consultation_done:
        return "free"

    if "kuliah" in text or "kampus" in text:
        return "campus"
    elif "jurusan smk" in text:
        return "smk"

    return "free"

# ================= CORE AI =================
def chat_with_ai(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 600
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            data=json.dumps(payload),
            timeout=20
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "AI: Server timeout."
    except requests.exceptions.ConnectionError:
        return "AI: Gagal terhubung ke server."
    except RequestException as e:
        return f"AI: Error API: {str(e)}"

# ================= STRUCTURED MODE =================
def run_structured_mode(mode):
    global consultation_done, last_mode

    consultation_done = True
    last_mode = mode

    messages = [{"role": "system", "content": SYSTEM_PROMPTS[mode]}]

    questions = AI_QUESTIONS_SMK if mode == "smk" else AI_QUESTIONS_CAMPUS

    print("\nAI: Oke. Aku bantu tentuin jurusan ya.")
    print("AI: Jawab pertanyaan ini biar hasilnya akurat.\n")

    for q in questions:
        print("AI:", q)
        answer = input("Kamu: ")
        messages.append({"role": "user", "content": answer})

    final_prompt = (
        "Rekomendasikan jurusan SMK yang cocok berdasarkan jawaban saya."
        if mode == "smk"
        else "Rekomendasikan jurusan kuliah yang cocok beserta alasannya dan kampusnya."
    )

    messages.append({"role": "user", "content": final_prompt})

    print("\nAI sedang menganalisis...\n")
    print("AI:", chat_with_ai(messages))
    print("\nSekarang kamu bisa tanya lanjutan tanpa ulang asesmen.\n")

# ================= MAIN =================
def main():
    show_banner()

    print("Ketik 'exit' untuk keluar.\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPTS["free"]}]

    while True:
        user_input = input("Kamu: ")

        if user_input.lower() == "exit":
            break

        detected_mode = detect_mode(user_input)

        if detected_mode in ["smk", "campus"]:
            run_structured_mode(detected_mode)
            messages = [{"role": "system", "content": SYSTEM_PROMPTS["free"]}]
            continue

        messages.append({"role": "user", "content": user_input})
        ai_reply = chat_with_ai(messages)
        messages.append({"role": "assistant", "content": ai_reply})

        print("AI:", ai_reply)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram dihentikan.")
