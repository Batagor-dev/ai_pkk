from dotenv import load_dotenv
import requests
import json
import os
from datetime import datetime
from requests.exceptions import RequestException
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import uuid
import re

# ================= INIT =================
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Store untuk menyimpan session data
user_sessions = {}

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

    print(CYAN + "KANUT Terminal AI Engine - API Mode" + RESET)
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

# ================= BPPI DATA EXTRACTOR =================
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
    
    # Deteksi pertanyaan tentang jurusan
    if any(word in text for word in ["jurusan", "prodi", "program", "rpl", "tkj", "akuntansi", "keahlian"]):
        extracted_data["type"] = "jurusan"
        extracted_data["found"] = True
        
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
            
            if "rpl" in text or "pengembangan perangkat lunak" in text:
                for j in jurusan_list:
                    if "pengembangan" in j["nama"].lower() or "rpl" in j["nama"].lower():
                        extracted_data["raw_data"]["specific_jurusan"] = j
                        break
            elif "tkj" in text or "jaringan" in text:
                for j in jurusan_list:
                    if "jaringan" in j["nama"].lower() or "tkj" in j["nama"].lower():
                        extracted_data["raw_data"]["specific_jurusan"] = j
                        break
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
            else:
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
        "Kamu adalah konselor jurusan SMK BPPI.\n"
        f"Gunakan data ini:\n{json.dumps(SCHOOL_DATA, ensure_ascii=False)}\n\n"

        "Gaya bicaramu santai, hangat, dan menggunakan bahasa gaul yang natural (lo, gue, nih, dll).\n"
        "Fokus pada 3 jurusan yang ada di SMK BPPI: RPL (Rekayasa Perangkat Lunak), TKJ (Teknik Komputer Jaringan), dan AKL (Akuntansi Keuangan Lembaga).\n\n"

        "Format jawaban:\n"
        "1. Ringkasan Profil User (berdasarkan jawaban sebelumnya)\n"
        "2. Rekomendasi Jurusan dari SMK BPPI (max 3)\n"
        "3. Alasan kuat tiap jurusan\n"
        "4. Alternatif\n"
        "5. Langkah selanjutnya\n"
        "6. Pertanyaan lanjutan\n\n"

        "Tambahkan confidence level (%) tiap jurusan.\n"
        "Jangan mengarang di luar data yang diberikan."
    ),

    "campus": (
        "Kamu adalah konselor jurusan kuliah.\n"
        "Gaya bicaramu santai, hangat, dan menggunakan bahasa gaul yang natural (lo, gue, nih, dll).\n\n"

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
        "temperature": 0.8
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
        return "Maaf, koneksi timeout nih. Coba tanyakan lagi ya!"
    except requests.exceptions.ConnectionError:
        return "Waduh, koneksi internetnya putus. Cek koneksi dulu yaa~"
    except RequestException as e:
        return f"Error teknis nih: {str(e)}"

# ================= NATURAL RESPONSE BUILDER =================
def build_natural_bppi_response(extracted_data, user_input):
    """Membangun response natural dari data mentah"""
    
    system_prompt = SYSTEM_PROMPTS["bppi_assistant"]
    
    data_summary = f"DATA MENTAH:\n{json.dumps(extracted_data.get('raw_data', {}), ensure_ascii=False, indent=2)}"
    
    user_message = f"""
Pertanyaan user: "{user_input}"

{data_summary}

Tolong buat jawaban yang NATURAL dan SANTAI berdasarkan data di atas. 
Gunakan gaya bicara seperti teman yang lagi ngasih info. 
Jangan copas data mentah, tapi sampaikan dengan bahasa yang enak dibaca.
Tambahkan sentuhan personal sesuai konteks pertanyaan.
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    return chat_with_ai(messages)

# ================= STRUCTURED MODE QUESTIONS =================
AI_QUESTIONS_SMK = [
    "Kalau boleh tau apa hobi kamu?",
    "Kamu punya skill apa yang paling kamu kuasai?",
    "Kamu lebih suka praktik atau teori?",
    "Kira kira nanti kamu pengen kerja sebagai apa?"
]

AI_QUESTIONS_CAMPUS = [
    "Kalau Boleh tau hal apa yang kamu suka lakuin?",
    "Kira kira bidang apa yang pengen kamu dalami?",
    "Kamu lebih suka yang logis atau kreatif?",
    "Kalau nanti kamu mau kerja di bidang apa nantinya?",
    "Kamu lebih suka riset atau langsung praktik?"
]

# ================= IS BPPI QUESTION =================
def is_asking_bppi(user_input):
    """Deteksi apakah user bertanya tentang BPPI"""
    text = user_input.lower()
    
    bppi_keywords = [
        "bppi", "smk bppi", "sekolah bppi", "info bppi",
        "jurusan bppi", "alamat bppi", "bppi dimana",
        "bppi jurusan", "bppi alamat", "tentang bppi",
        "di bppi"
    ]
    
    for keyword in bppi_keywords:
        if keyword in text:
            return True
    
    if any(word in text for word in ["jurusan", "alamat", "fasilitas", "spp", "biaya", "guru", "staff"]):
        if "bppi" in text or "smk" in text or "sekolah" in text:
            return True
    
    return False

# ================= API ENDPOINTS =================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'school_data_loaded': bool(SCHOOL_DATA)
    })

@app.route('/api/start-session', methods=['POST'])
def start_session():
    session_id = str(uuid.uuid4())
    user_sessions[session_id] = {
        'messages': [{"role": "system", "content": SYSTEM_PROMPTS["free"]}],
        'consultation_done': False,
        'user_profile': {},
        'mode': 'free',
        'created_at': datetime.now().isoformat(),
        'structured_messages': [],
        'current_question_index': 0,
        'questions': [],
        'awaiting_consultation_response': False
    }
    
    return jsonify({
        'session_id': session_id,
        'message': 'Session started successfully',
        'banner': {
            'title': 'KANUT Terminal AI Engine',
            'environment': 'Development',
            'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Endpoint utama untuk chat dengan AI"""
    data = request.json
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    session_id = data.get('session_id')
    user_input = data['message']
    
    # Buat session baru jika tidak ada session_id
    if not session_id or session_id not in user_sessions:
        session_id = str(uuid.uuid4())
        user_sessions[session_id] = {
            'messages': [{"role": "system", "content": SYSTEM_PROMPTS["free"]}],
            'consultation_done': False,
            'user_profile': {},
            'mode': 'free',
            'created_at': datetime.now().isoformat(),
            'structured_messages': [],
            'current_question_index': 0,
            'questions': [],
            'awaiting_consultation_response': False
        }
    
    session_data = user_sessions[session_id]
    
    # ========== PRIORITAS: CEK BPPI ==========
    # Jika user bertanya tentang BPPI, langsung jawab dengan data sekolah
    if is_asking_bppi(user_input):
        extracted_data = extract_bppi_data(user_input)
        
        if extracted_data.get("found"):
            natural_response = build_natural_bppi_response(extracted_data, user_input)
            
            session_data['messages'].append({"role": "user", "content": user_input})
            session_data['messages'].append({"role": "assistant", "content": natural_response})
            
            # Reset consultation mode jika sedang aktif
            session_data['awaiting_consultation_response'] = False
            session_data['consultation_done'] = False
            
            return jsonify({
                'session_id': session_id,
                'reply': natural_response,
                'mode': 'bppi',
                'consultation_done': session_data['consultation_done']
            })
    
    # ========== HANDLE STRUCTURED MODE (AKTIF) ==========
    # Cek apakah sedang dalam sesi konsultasi yang aktif
    if session_data.get('awaiting_consultation_response') and session_data.get('mode') in ["smk", "campus"]:
        # Ini adalah jawaban dari pertanyaan konsultasi
        current_index = session_data.get('current_question_index', 0)
        questions = session_data.get('questions', [])
        
        if current_index < len(questions):
            # Simpan jawaban user
            current_question = questions[current_index]
            session_data['user_profile'][current_question] = user_input
            session_data['structured_messages'].append({"role": "user", "content": user_input})
            
            # Lanjut ke pertanyaan berikutnya
            next_index = current_index + 1
            
            if next_index < len(questions):
                # Masih ada pertanyaan, kirim pertanyaan berikutnya
                session_data['current_question_index'] = next_index
                next_question = questions[next_index]
                
                return jsonify({
                    'session_id': session_id,
                    'mode': session_data['mode'],
                    'type': 'structured_next',
                    'question': next_question,
                    'question_index': next_index,
                    'total_questions': len(questions),
                    'consultation_done': session_data['consultation_done'],
                    'awaiting_response': True
                })
            else:
                # Selesai semua pertanyaan, berikan rekomendasi
                session_data['structured_messages'].append({
                    "role": "user",
                    "content": f"Berdasarkan profil ini: {json.dumps(session_data['user_profile'], ensure_ascii=False)}\nBerikan rekomendasi jurusan yang paling cocok dengan gaya santai dan natural."
                })
                
                # Panggil AI untuk rekomendasi
                reply = chat_with_ai(session_data['structured_messages'])
                
                # Reset consultation mode
                session_data['consultation_done'] = True
                session_data['awaiting_consultation_response'] = False
                session_data['mode'] = 'free'
                session_data['current_question_index'] = 0
                
                # Simpan ke history
                session_data['messages'].append({"role": "assistant", "content": reply})
                
                return jsonify({
                    'session_id': session_id,
                    'mode': 'free',
                    'type': 'structured_complete',
                    'reply': reply,
                    'consultation_done': session_data['consultation_done'],
                    'user_profile': session_data['user_profile']
                })
    
    # ========== DETEKSI MODE KONSULTASI (BARU) ==========
    # Cek apakah user minta rekomendasi jurusan
    consultation_keywords = [
        "rekomendasi jurusan", "jurusan yang cocok", "mau masuk jurusan apa",
        "pilih jurusan", "bingung jurusan", "jurusan smk", "masuk smk jurusan",
        "rekomendasi jurusan buat aku", "kasih rekomendasi jurusan"
    ]
    
    is_consultation_request = any(keyword in user_input.lower() for keyword in consultation_keywords)
    
    # Cek apakah ini tentang SMK atau kuliah
    is_smk_related = any(word in user_input.lower() for word in ["smk", "sekolah kejuruan"])
    is_campus_related = any(word in user_input.lower() for word in ["kuliah", "universitas", "kampus", "s1"])
    
    # Jika minta rekomendasi dan TIDAK menyebut BPPI secara spesifik
    if is_consultation_request and not is_asking_bppi(user_input):
        # Default ke SMK karena ini asisten SMK BPPI
        mode = "smk"
        
        # Tapi kalau user spesifik minta kuliah, kasih kuliah
        if is_campus_related and not is_smk_related:
            mode = "campus"
        
        # Setup structured consultation
        session_data['mode'] = mode
        session_data['consultation_done'] = False
        session_data['awaiting_consultation_response'] = True
        session_data['current_question_index'] = 0
        session_data['questions'] = AI_QUESTIONS_SMK if mode == "smk" else AI_QUESTIONS_CAMPUS
        session_data['user_profile'] = {}
        session_data['structured_messages'] = [{"role": "system", "content": SYSTEM_PROMPTS[mode]}]
        
        # Kirim pertanyaan pertama
        first_question = session_data['questions'][0]
        
        return jsonify({
            'session_id': session_id,
            'mode': mode,
            'type': 'structured_start',
            'question': first_question,
            'question_index': 0,
            'total_questions': len(session_data['questions']),
            'consultation_done': session_data['consultation_done'],
            'awaiting_response': True
        })
    
    # ========== FREE MODE ==========
    # Jika bukan BPPI dan bukan konsultasi, jalanin free mode
    session_data['messages'].append({"role": "user", "content": user_input})
    reply = chat_with_ai(session_data['messages'])
    session_data['messages'].append({"role": "assistant", "content": reply})
    
    return jsonify({
        'session_id': session_id,
        'reply': reply,
        'mode': 'free',
        'consultation_done': session_data['consultation_done']
    })

@app.route('/api/bppi/info', methods=['POST'])
def bppi_info():
    """Endpoint untuk mendapatkan informasi BPPI dengan natural response"""
    data = request.json
    user_input = data.get('query', '')
    
    if not user_input:
        return jsonify({'error': 'Query is required'}), 400
    
    extracted_data = extract_bppi_data(user_input)
    
    if extracted_data.get("found"):
        natural_response = build_natural_bppi_response(extracted_data, user_input)
        return jsonify({
            'query': user_input,
            'reply': natural_response,
            'school_data_available': bool(SCHOOL_DATA),
            'extracted_type': extracted_data.get('type')
        })
    else:
        return jsonify({
            'query': user_input,
            'reply': 'Maaf, data tentang itu belum tersedia nih.',
            'school_data_available': bool(SCHOOL_DATA)
        })

@app.route('/api/bppi/jurusan', methods=['GET'])
def bppi_jurusan():
    if not SCHOOL_DATA or 'jurusan' not in SCHOOL_DATA:
        return jsonify({'error': 'Data jurusan tidak tersedia'}), 404
    
    jurusan_list = []
    for j in SCHOOL_DATA['jurusan']:
        if isinstance(j, dict):
            jurusan_list.append({
                'nama': j.get('nama_jurusan', 'Unknown'),
                'deskripsi': j.get('deskripsi_singkat', ''),
                'skill_utama': j.get('skill_utama', [])[:3],
                'cocok_untuk': j.get('cocok_untuk_minat', [])
            })
        else:
            jurusan_list.append({'nama': j})
    
    return jsonify({
        'jurusan': jurusan_list,
        'total': len(jurusan_list)
    })

@app.route('/api/bppi/staff', methods=['GET'])
def bppi_staff():
    if not SCHOOL_DATA or 'staff_sekolah' not in SCHOOL_DATA:
        return jsonify({'error': 'Data staff tidak tersedia'}), 404
    
    staff = SCHOOL_DATA['staff_sekolah']
    
    result = {
        'total': len(staff),
        'kepala_sekolah': [],
        'wakasek': [],
        'kaprodi': [],
        'guru': [],
        'lainnya': []
    }
    
    for s in staff:
        item = {
            'nama': s.get('nama', 'Unknown'),
            'jabatan': s.get('jabatan', []),
            'mata_pelajaran': s.get('mata_pelajaran', [])
        }
        
        if 'Kepala Sekolah' in item['jabatan']:
            result['kepala_sekolah'].append(item)
        elif any('Wakasek' in j for j in item['jabatan']):
            result['wakasek'].append(item)
        elif any('Kaprodi' in j for j in item['jabatan']):
            result['kaprodi'].append(item)
        elif item['mata_pelajaran']:
            result['guru'].append(item)
        else:
            result['lainnya'].append(item)
    
    return jsonify(result)

@app.route('/api/bppi/biaya', methods=['GET'])
def bppi_biaya():
    if not SCHOOL_DATA or 'biaya_pendidikan' not in SCHOOL_DATA:
        return jsonify({'error': 'Data biaya tidak tersedia'}), 404
    
    biaya = SCHOOL_DATA['biaya_pendidikan']
    
    formatted_biaya = {
        'spp_bulanan': format_currency(biaya.get('spp_bulanan')),
        'pendaftaran': {}
    }
    
    if 'pendaftaran' in biaya:
        if 'kelas_reguler' in biaya['pendaftaran']:
            formatted_biaya['pendaftaran']['kelas_reguler'] = format_currency(biaya['pendaftaran']['kelas_reguler'])
        if 'kelas_industri_axioo' in biaya['pendaftaran']:
            formatted_biaya['pendaftaran']['kelas_industri_axioo'] = format_currency(biaya['pendaftaran']['kelas_industri_axioo'])
    
    if 'catatan' in biaya:
        formatted_biaya['catatan'] = biaya['catatan']
    
    return jsonify(formatted_biaya)

@app.route('/api/bppi/kontak', methods=['GET'])
def bppi_kontak():
    if not SCHOOL_DATA or 'kontak_sekolah' not in SCHOOL_DATA:
        return jsonify({'error': 'Data kontak tidak tersedia'}), 404
    
    return jsonify(SCHOOL_DATA['kontak_sekolah'])

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    if session_id not in user_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session_data = user_sessions[session_id]
    return jsonify({
        'session_id': session_id,
        'consultation_done': session_data['consultation_done'],
        'mode': session_data.get('mode', 'free'),
        'created_at': session_data.get('created_at'),
        'message_count': len(session_data.get('messages', []))
    })

@app.route('/api/session/<session_id>/history', methods=['GET'])
def get_chat_history(session_id):
    if session_id not in user_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session_data = user_sessions[session_id]
    
    history = []
    for msg in session_data.get('messages', []):
        if msg['role'] in ['user', 'assistant']:
            history.append({
                'role': msg['role'],
                'content': msg['content']
            })
    
    return jsonify({
        'session_id': session_id,
        'history': history
    })

@app.route('/api/session/<session_id>/reset', methods=['POST'])
def reset_session(session_id):
    if session_id not in user_sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    user_sessions[session_id] = {
        'messages': [{"role": "system", "content": SYSTEM_PROMPTS["free"]}],
        'consultation_done': False,
        'user_profile': {},
        'mode': 'free',
        'created_at': datetime.now().isoformat(),
        'structured_messages': [],
        'current_question_index': 0,
        'questions': [],
        'awaiting_consultation_response': False
    }
    
    return jsonify({
        'session_id': session_id,
        'message': 'Session reset successfully'
    })

# ================= CLEANUP SESSIONS =================
@app.before_request
def cleanup_sessions():
    """Bersihkan session yang sudah tua (lebih dari 1 jam)"""
    current_time = datetime.now()
    to_delete = []
    
    for session_id, session_data in user_sessions.items():
        if 'created_at' in session_data:
            created_time = datetime.fromisoformat(session_data['created_at'])
            if (current_time - created_time).seconds > 3600:
                to_delete.append(session_id)
    
    for session_id in to_delete:
        del user_sessions[session_id]

# ================= MAIN =================
def main():
    show_banner()
    print("🚀 API Server running on http://localhost:5000")
    print("📚 API Documentation:")
    print("   GET  /api/health                  - Cek status API")
    print("   POST /api/start-session           - Mulai session baru")
    print("   POST /api/chat                    - Chat dengan AI (auto detect BPPI & consultation)")
    print("   POST /api/bppi/info               - Info BPPI dengan natural response")
    print("   GET  /api/bppi/jurusan            - Daftar jurusan")
    print("   GET  /api/bppi/staff              - Daftar staff/guru")
    print("   GET  /api/bppi/biaya              - Info biaya")
    print("   GET  /api/bppi/kontak             - Info kontak")
    print("   GET  /api/session/<id>            - Info session")
    print("   GET  /api/session/<id>/history    - History chat")
    print("   POST /api/session/<id>/reset      - Reset session")
    print("\n✨ New Features:")
    print("   • Priority BPPI questions (answered with school data)")
    print("   • Active consultation mode with follow-up questions")
    print("   • Smart mode detection based on keywords")
    print("   • Natural responses for BPPI inquiries")
    print("   • Structured Q&A for SMK/Campus consultation")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped.")