from dotenv import load_dotenv
import requests
import json
import os
from datetime import datetime
from requests.exceptions import RequestException
import re

# ================= INIT =================
load_dotenv()

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
    try:
        with open("bppi.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: File bppi.json tidak ditemukan!")
        return {}
    except json.JSONDecodeError:
        print("Warning: Format JSON tidak valid!")
        return {}

SCHOOL_DATA = load_school_data()

# ================= BPPI DATA EXTRACTOR (MENTAH) =================
def format_currency(amount):
    """Format angka ke format Rupiah"""
    if amount is None:
        return "informasi lebih lanjut"
    try:
        return f"Rp {amount:,.0f}".replace(",", ".")
    except:
        return str(amount)

def extract_bppi_data(user_input):
    """
    MENGAMBIL DATA MENTAH DARI BPPI
    Output: Dictionary dengan data mentah yang ditemukan
    """
    if not SCHOOL_DATA:
        return {"error": "Data tidak tersedia"}
    
    text = user_input.lower()
    extracted_data = {
        "found": False,
        "type": None,
        "raw_data": {},
        "query_context": text
    }
    
    # ===== DETEKSI JENIS PERTANYAAN =====
    
    # Deteksi pertanyaan tentang jurusan
    if any(word in text for word in ["jurusan", "prodi", "program", "rpl", "tkj", "akuntansi", "keahlian"]):
        extracted_data["type"] = "jurusan"
        extracted_data["found"] = True
        
        # Ambil data jurusan
        if "jurusan" in SCHOOL_DATA:
            jurusan_list = []
            for j in SCHOOL_DATA["jurusan"]:
                if isinstance(j, dict):
                    jurusan_info = {
                        "nama": j.get("nama_jurusan", ""),
                        "deskripsi": j.get("deskripsi_singkat", ""),
                        "skill": j.get("skill_utama", []),
                        "minat": j.get("cocok_untuk_minat", [])
                    }
                    jurusan_list.append(jurusan_info)
                else:
                    jurusan_list.append({"nama": j})
            
            extracted_data["raw_data"]["jurusan"] = jurusan_list
            
            # Jika spesifik RPL
            if "rpl" in text or "pengembangan perangkat lunak" in text:
                for j in jurusan_list:
                    if "pengembangan" in j["nama"].lower() or "rpl" in j["nama"].lower():
                        extracted_data["raw_data"]["specific_jurusan"] = j
                        break
            
            # Jika spesifik TKJ
            elif "tkj" in text or "jaringan" in text:
                for j in jurusan_list:
                    if "jaringan" in j["nama"].lower() or "tkj" in j["nama"].lower():
                        extracted_data["raw_data"]["specific_jurusan"] = j
                        break
            
            # Jika spesifik Akuntansi
            elif "akuntansi" in text or "akl" in text:
                for j in jurusan_list:
                    if "akuntansi" in j["nama"].lower():
                        extracted_data["raw_data"]["specific_jurusan"] = j
                        break
    
    # Deteksi pertanyaan tentang biaya
    elif any(word in text for word in ["biaya", "spp", "uang", "mahal", "pendaftaran"]):
        extracted_data["type"] = "biaya"
        extracted_data["found"] = True
        
        if "biaya_pendidikan" in SCHOOL_DATA:
            biaya = SCHOOL_DATA["biaya_pendidikan"]
            extracted_data["raw_data"]["biaya"] = {
                "spp_bulanan": biaya.get("spp_bulanan"),
                "pendaftaran": biaya.get("pendaftaran", {}),
                "catatan": biaya.get("catatan", "")
            }
    
    # Deteksi pertanyaan tentang guru/staff
    elif any(word in text for word in ["guru", "staff", "pengajar", "teacher", "kepala sekolah", "wakasek", "kaprodi"]):
        extracted_data["type"] = "staff"
        extracted_data["found"] = True
        
        if "staff_sekolah" in SCHOOL_DATA:
            staff_list = []
            for s in SCHOOL_DATA["staff_sekolah"]:
                staff_info = {
                    "nama": s.get("nama", ""),
                    "jabatan": s.get("jabatan", []),
                    "mata_pelajaran": s.get("mata_pelajaran", [])
                }
                staff_list.append(staff_info)
            
            extracted_data["raw_data"]["staff"] = staff_list
            
            # Filter spesifik berdasarkan mata pelajaran
            if "bahasa indonesia" in text:
                filtered = [s for s in staff_list if any("Bahasa Indonesia" in m for m in s["mata_pelajaran"])]
                if filtered:
                    extracted_data["raw_data"]["filtered_staff"] = filtered
            
            elif "bahasa inggris" in text:
                filtered = [s for s in staff_list if any("Bahasa Inggris" in m for m in s["mata_pelajaran"])]
                if filtered:
                    extracted_data["raw_data"]["filtered_staff"] = filtered
            
            elif "matematika" in text:
                filtered = [s for s in staff_list if any("Matematika" in m for m in s["mata_pelajaran"])]
                if filtered:
                    extracted_data["raw_data"]["filtered_staff"] = filtered
            
            # Filter spesifik berdasarkan nama
            else:
                # Cek apakah ada nama yang disebut
                name_pattern = r'\b(asep|dede|anggi|gilang|wahyudi|dinny|elsa|guruh|iwan|nurwita|penny|pravita|rina|salsabila|talitha|yogie)\b'
                name_match = re.search(name_pattern, text)
                if name_match:
                    searched_name = name_match.group(1)
                    filtered = [s for s in staff_list if searched_name in s["nama"].lower()]
                    if filtered:
                        extracted_data["raw_data"]["filtered_staff"] = filtered
                        extracted_data["raw_data"]["searched_name"] = searched_name
    
    # Deteksi pertanyaan tentang fasilitas/keunggulan
    elif any(word in text for word in ["fasilitas", "unggulan", "kerjasama", "prestasi"]):
        extracted_data["type"] = "keunggulan"
        extracted_data["found"] = True
        
        if "keunggulan_sekolah" in SCHOOL_DATA:
            unggul = SCHOOL_DATA["keunggulan_sekolah"]
            extracted_data["raw_data"]["keunggulan"] = {
                "fasilitas": unggul.get("fasilitas_unggulan", []),
                "program": unggul.get("program_unggulan", []),
                "kerjasama": unggul.get("kerja_sama", [])
            }
    
    # Deteksi pertanyaan tentang kontak
    elif any(word in text for word in ["kontak", "telepon", "wa", "email", "website", "hubungi"]):
        extracted_data["type"] = "kontak"
        extracted_data["found"] = True
        
        if "kontak_sekolah" in SCHOOL_DATA:
            extracted_data["raw_data"]["kontak"] = SCHOOL_DATA["kontak_sekolah"]
    
    # Deteksi pertanyaan tentang prospek lulusan
    elif any(word in text for word in ["lulusan", "kerja", "karir", "prospek", "kerja apa"]):
        extracted_data["type"] = "prospek"
        extracted_data["found"] = True
        
        if "output_lulusan" in SCHOOL_DATA:
            extracted_data["raw_data"]["prospek"] = SCHOOL_DATA["output_lulusan"]
    
    # Deteksi pertanyaan tentang alamat/identitas
    elif any(word in text for word in ["alamat", "lokasi", "dimana", "profil", "identitas"]):
        extracted_data["type"] = "identitas"
        extracted_data["found"] = True
        
        if "identitas_sekolah" in SCHOOL_DATA:
            extracted_data["raw_data"]["identitas"] = SCHOOL_DATA["identitas_sekolah"]
    
    # Default: ambil info umum
    else:
        extracted_data["type"] = "general"
        extracted_data["found"] = True
        
        # Ambil info ringkas
        if "identitas_sekolah" in SCHOOL_DATA:
            extracted_data["raw_data"]["identitas"] = SCHOOL_DATA["identitas_sekolah"]
        if "jurusan" in SCHOOL_DATA:
            jurusan_singkat = []
            for j in SCHOOL_DATA["jurusan"][:3]:
                if isinstance(j, dict):
                    jurusan_singkat.append(j.get("nama_jurusan", ""))
                else:
                    jurusan_singkat.append(j)
            extracted_data["raw_data"]["jurusan_singkat"] = jurusan_singkat
        if "biaya_pendidikan" in SCHOOL_DATA:
            extracted_data["raw_data"]["spp"] = SCHOOL_DATA["biaya_pendidikan"].get("spp_bulanan")
    
    return extracted_data

# ================= SYSTEM PROMPTS =================
SYSTEM_PROMPTS = {
    "free": (
        "Kamu adalah AI companion yang berperan sebagai teman, konsultan, dan pendengar yang suportif.\n"
        "Gaya bicaramu santai, hangat, natural, dan tidak kaku seperti robot.\n"
        "Fokus utama: membantu user berpikir lebih jernih, merasa didengar, dan menemukan arah.\n"
        "\n"
        "PRINSIP UTAMA:\n"
        "- Jangan hanya menjawab—bangun percakapan.\n"
        "- Dengarkan maksud user, bukan hanya kata-katanya.\n"
        "- Respon harus terasa manusiawi, bukan template.\n"
        "- Jangan menghakimi, jangan menggurui.\n"
        "- Bantu user pelan-pelan, bukan langsung dikasih jawaban final.\n"
        "\n"
        "MODE OTOMATIS (adapt sesuai kondisi user):\n"
        "\n"
        "1. MODE TEMAN (default):\n"
        "- Kalau user santai atau ngobrol biasa\n"
        "- Respon ringan, cair, dan relate\n"
        "- Tambahkan opini atau insight kecil\n"
        "- Boleh lempar pertanyaan ringan biar lanjut ngobrol\n"
        "\n"
        "2. MODE KONSULTAN:\n"
        "- Jika user butuh keputusan (jurusan, karir, pilihan hidup)\n"
        "- Gali dulu: minat, kebiasaan, kelebihan\n"
        "- Berikan opsi, bukan jawaban mutlak\n"
        "- Jelaskan plus-minus tiap opsi\n"
        "- Arahkan dengan logika + relevansi ke kondisi user\n"
        "\n"
        "3. MODE SUPPORT (psikologis ringan):\n"
        "- Jika user terlihat stres, overthinking, sedih, bingung\n"
        "- Validasi perasaan tanpa berlebihan\n"
        "- Gunakan bahasa yang menenangkan\n"
        "- Hindari kata-kata menghakimi\n"
        "- Bantu user melihat situasi dengan sudut pandang yang lebih sehat\n"
        "- Jangan berpura-pura sebagai psikolog profesional\n"
        "\n"
        "TEKNIK INTERAKSI:\n"
        "- Gunakan pertanyaan terbuka ('menurut lo gimana?', 'yang paling bikin lo kepikiran apa?')\n"
        "- Gunakan pilihan sederhana (A/B) kalau user bingung\n"
        "- Gunakan analogi biar mudah dipahami\n"
        "- Jangan terlalu panjang, tapi tetap bermakna\n"
        "\n"
        "HAL YANG HARUS DIHINDARI:\n"
        "- Jawaban kaku seperti FAQ\n"
        "- Terlalu formal atau terlalu dingin\n"
        "- Langsung menyimpulkan tanpa memahami user\n"
        "- Memberi diagnosis mental atau medis\n"
        "\n"
        "GOAL AKHIR:\n"
        "User merasa: didengar, dipahami, dan terbantu untuk melangkah lebih jelas.\n"
    ),

    "smk": (
        "Kamu adalah konselor jurusan SMK.\n"
        f"Gunakan data ini:\n{json.dumps(SCHOOL_DATA, ensure_ascii=False)}\n\n"

        "Format jawaban:\n"
        "1. Ringkasan Profil User\n"
        "2. Rekomendasi Jurusan (max 3)\n"
        "3. Alasan kuat tiap jurusan\n"
        "4. Alternatif\n"
        "5. Langkah selanjutnya\n"
        "6. Pertanyaan lanjutan\n\n"

        "Tambahkan confidence level (%) tiap jurusan.\n"
        "Jangan mengarang di luar data."
    ),

    "campus": (
        "Kamu adalah konselor jurusan kuliah.\n"

        "Format jawaban:\n"
        "1. Ringkasan Profil User\n"
        "2. Rekomendasi Jurusan + Kampus\n"
        "3. Alasan kuat\n"
        "4. Alternatif\n"
        "5. Langkah konkret\n"
        "6. Pertanyaan lanjutan\n\n"

        "Tambahkan confidence level (%)."
    ),
    
    "bppi_assistant": (
        "Kamu adalah asisten virtual SMK BPPI yang ramah, informatif, dan natural.\n"
        "Gaya bicaramu seperti teman yang ngasih info—hangat, nggak kaku, dan sesuai konteks.\n"
        "\n"
        "ATURAN NATURAL:\n"
        "- Jangan pakai kata pembuka yang sama terus (hindari 'oh iya nih' berkali-kali)\n"
        "- Variasikan pembuka sesuai konteks:\n"
        "  * Kalau user lagi nanya sesuatu yang baru → 'Nah, kalau itu...' / 'Oke, ini dia...' / 'Buat yang ini...'\n"
        "  * Kalau nyambung dari obrolan sebelumnya → 'Lanjut ya...' / 'Nah, dari tadi lo tanya...' / 'Oke, sekarang...'\n"
        "  * Kalau user lagi butuh info cepat → 'Ini dia...' / 'Gampang kok...' / 'Singkatnya...'\n"
        "  * Kadang bisa langsung ke poin tanpa pembuka kalau lagi cair\n"
        "\n"
        "GAYA BICARA:\n"
        "- Gunakan 'lo', 'gue', 'nih', 'dong', 'deh' secukupnya biar akrab\n"
        "- Sesekali kasih reaksi ringan kayak 'wah', 'nah', 'oh gitu', 'iya bener'\n"
        "- Kalau info penting, sampaikan dengan jelas tanpa bertele-tele\n"
        "- Tambahkan pertanyaan balik yang relevan di akhir biar obrolan lanjut\n"
        "\n"
        "FORMAT JAWABAN NATURAL:\n"
        "Jangan seperti ini (kaku):\n"
        "- 'Oh iya nih, alamat SMK BPPI...' (diulang terus)\n"
        "- 'Oh iya nih, soal biaya...' (setiap kali)\n"
        "\n"
        "Lebih baik seperti ini (variatif):\n"
        "- 'Nah, alamatnya tuh di Jl. Adipati Agung...'\n"
        "- 'Oke, buat biaya, gue kasih tau ya...'\n"
        "- 'Gampang kok nyarinya, lo tinggal...'\n"
        "- Langsung jawab: 'Jl. Adipati Agung No.23, Baleendah.' (tanpa pembuka berlebihan)\n"
        "\n"
        "PRINSIP:\n"
        "- Gunakan data yang diberikan dengan natural, jangan copas mentah\n"
        "- Susun informasi sesuai kebutuhan user\n"
        "- Jangan terlalu panjang, tapi informasinya padat\n"
        "- Akhiri dengan pertanyaan ringan yang relate ke konteks\n"
        "\n"
        "Contoh response bagus:\n"
        "User: 'alamat sekolahnya?'\n"
        "AI: 'Jl. Adipati Agung No.23, Baleendah. Dari alun-alun Baleendah cuma 5 menitan naik motor. Mau daftar atau emang lagi nyari lokasinya?'\n"
        "\n"
        "User: 'biaya spp berapa?'\n"
        "AI: 'SPP bulanan Rp 250.000. Tapi ada juga biaya pendaftaran buat reguler sama kelas industri. Lo mau cari info yang mana? Biar gue jelasin lebih detail.'\n"
    )
}

# ================= AI CHAT FUNCTION =================
def chat_with_ai(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 700,
        "temperature": 0.8  # Tambah sedikit kreativitas untuk response natural
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
        return "AI: Maaf, koneksi timeout nih. Coba tanyakan lagi ya!"
    except requests.exceptions.ConnectionError:
        return "AI: Waduh, koneksi internetnya putus. Cek koneksi dulu yaa~"
    except RequestException as e:
        return f"AI: Error teknis nih: {str(e)}"

# ================= NATURAL RESPONSE BUILDER =================
def build_natural_bppi_response(extracted_data, user_input):
    """
    MEMBANGUN RESPONSE NATURAL DARI DATA MENTAH
    Data mentah → diproses → response natural
    """
    
    data_type = extracted_data.get("type", "general")
    raw_data = extracted_data.get("raw_data", {})
    context = extracted_data.get("query_context", "")
    
    # Siapkan prompt untuk AI dengan data mentah
    system_prompt = SYSTEM_PROMPTS["bppi_assistant"]
    
    # Bangun pesan untuk AI dengan data mentah
    data_summary = f"DATA MENTAH:\n{json.dumps(raw_data, ensure_ascii=False, indent=2)}"
    
    user_message = f"""
Pertanyaan user: "{user_input}"

{data_summary}

Tolong buat jawaban yang NATURAL dan SANTAI berdasarkan data di atas. 
Gunakan gaya bicara seperti teman yang lagi ngasih info. 
Jangan copas data mentah, tapi sampaikan dengan bahasa yang enak dibaca.
Tambahkan sentuhan personal sesuai konteks pertanyaan.

Contoh gaya:
- "Oh iya nih, soal jurusan RPL..."
- "Wah, lo nanya biaya ya? Oke gue kasih tau..."
- "Nah buat guru Bahasa Indonesia, ada nih..."
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    return chat_with_ai(messages)

# ================= MODE DETECTION =================
consultation_done = False
user_profile = {}

def detect_mode(user_input):
    global consultation_done
    text = user_input.lower()

    if consultation_done:
        return "free"

    if any(word in text for word in [
        "bingung jurusan",
        "pilih jurusan",
        "rekomendasi jurusan",
        "mau masuk jurusan apa",
        "jurusan apa yang cocok"
    ]):
        if "smk" in text:
            return "smk"
        return "campus"

    return "free"

# ================= STRUCTURED MODE =================
AI_QUESTIONS_SMK = [
    "Apa hobi utama kamu?",
    "Skill apa yang paling kamu kuasai?",
    "Kamu lebih suka praktik atau teori?"
]

AI_QUESTIONS_CAMPUS = [
    "Hal apa yang kamu suka lakuin?",
    "Bidang apa yang pengen kamu dalami?",
    "Lebih suka yang logis atau kreatif?",
    "Mau kerja di bidang apa nantinya?",
    "Lebih suka riset atau langsung praktik?"
]

def run_structured_mode(mode):
    global consultation_done, user_profile

    consultation_done = True
    user_profile = {}

    messages = [{"role": "system", "content": SYSTEM_PROMPTS[mode]}]

    questions = AI_QUESTIONS_SMK if mode == "smk" else AI_QUESTIONS_CAMPUS

    print("\nAI: Oke, gue bantu tentuin arah kamu yaa.")
    print("AI: Jawab santai aja, gue bakal analisa dengan hati-hati.\n")

    for q in questions:
        print("AI:", q)
        answer = input("Kamu: ")
        user_profile[q] = answer
        messages.append({"role": "user", "content": answer})

    messages.append({
        "role": "user",
        "content": f"Profil saya: {json.dumps(user_profile, ensure_ascii=False)}\nBerikan rekomendasi terbaik."
    })

    print("\nAI: Lagi mikir berdasarkan jawaban kamu...\n")
    result = chat_with_ai(messages)
    print("AI:\n", result)

    feedback = input("\nAI: Ini membantu? (ya/tidak): ")

    if feedback.lower() == "tidak":
        detail = input("AI: Bagian mana yang kurang cocok?: ")
        messages.append({"role": "user", "content": f"Perbaiki: {detail}"})

        print("\nAI: Oke gue refine lagi...\n")
        print("AI:\n", chat_with_ai(messages))

    follow = input("\nAI: Mau diperdalam lebih lanjut atau cukup?: ")
    messages.append({"role": "user", "content": follow})
    print("AI:\n", chat_with_ai(messages))

# ================= IS BPPI QUESTION =================
def is_asking_bppi(user_input):
    """Deteksi apakah user bertanya tentang BPPI"""
    text = user_input.lower()
    
    bppi_keywords = [
        "bppi", "smk bppi", "sekolah bppi", "info bppi",
        "jurusan bppi", "alamat bppi", "bppi dimana",
        "bppi jurusan", "bppi alamat", "tentang bppi",
        "di bppi", "smk itu", "sekolah ini"
    ]
    
    for keyword in bppi_keywords:
        if keyword in text:
            return True
    
    # Cek pertanyaan spesifik
    if any(word in text for word in ["jurusan", "alamat", "fasilitas", "spp", "biaya", "guru", "staff"]):
        # Pastikan konteksnya tentang sekolah/BPPI
        if "bppi" in text or "smk" in text or "sekolah" in text:
            return True
    
    return False

# ================= MAIN =================
def main():
    show_banner()

    print("Halo! 👋 Gue Kanut, teman ngobrol kamu.")
    print("Bisa ngobrol santai, konsultasi jurusan, atau tanya info SMK BPPI.")
    print("Ketik 'exit' kapan aja buat keluar.\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPTS["free"]}]

    while True:
        user_input = input("Kamu: ")

        if user_input.lower() == "exit":
            print("\nAI: Sampai jumpa! Semoga harimu menyenangkan~ ✨")
            break

        # ===== FLOW: User Input → Extract Data → AI Natural Response =====
        if is_asking_bppi(user_input):
            # STEP 1: Extract data mentah dari BPPI
            extracted_data = extract_bppi_data(user_input)
            
            # STEP 2: Build natural response from raw data
            if extracted_data.get("found"):
                natural_response = build_natural_bppi_response(extracted_data, user_input)
                print("AI:", natural_response)
            else:
                print("AI: Maaf, data tentang itu belum tersedia nih. Ada yang lain yang mau ditanyakan?")
            
            continue

        # ===== HANDLE CONSULTATION MODE =====
        mode = detect_mode(user_input)

        if mode in ["smk", "campus"]:
            run_structured_mode(mode)
            # Reset messages after consultation
            messages = [{"role": "system", "content": SYSTEM_PROMPTS["free"]}]
            continue

        # ===== FREE MODE (Normal Chat) =====
        messages.append({"role": "user", "content": user_input})
        reply = chat_with_ai(messages)
        messages.append({"role": "assistant", "content": reply})

        print("AI:", reply)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAI: Dadah~ Sampai jumpa lagi! 👋")