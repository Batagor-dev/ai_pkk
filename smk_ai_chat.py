import requests
import json

API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Pertanyaan awal AI untuk personalisasi siswa
ai_questions = [
    "Halo! Aku AI yang akan bantu kamu menemukan jurusan SMK yang cocok. Sebelum itu, boleh tahu hobimu apa saja?",
    "Apa yang biasanya kamu sukai kerjakan di waktu luang?",
    "Skill atau kemampuan khusus apa yang kamu punya?",
    "Apakah kamu lebih suka kerja yang praktis langsung, atau lebih suka teori dan analisis?",
]

def chat_with_ai(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-5.2",
        "messages": messages,
        "max_tokens": 200
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        data = response.json()
        # ambil content terakhir dari AI
        return data["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"

def main():
    print("=== AI Rekomendasi Jurusan SMK ===")
    print("AI akan menanyakan beberapa hal tentang kamu agar bisa rekomendasikan jurusan SMK yang cocok.\n")

    messages = []

    for question in ai_questions:
        # AI nanya
        messages.append({"role": "assistant", "content": question})
        print(f"AI: {question}")

        # User jawab
        answer = input("Kamu: ")
        messages.append({"role": "user", "content": answer})

    # Gabungkan semua jawaban user untuk minta rekomendasi final
    messages.append({
        "role": "user",
        "content": "Berdasarkan jawaban di atas, rekomendasikan jurusan SMK yang paling cocok untuk saya beserta alasannya secara singkat."
    })

    print("\nAI sedang menganalisis jawabanmu...\n")
    ai_response = chat_with_ai(messages)
    print(f"AI: {ai_response}")

if __name__ == "__main__":
    main()
