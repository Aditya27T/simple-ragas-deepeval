import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

# Load API Key dari .env
load_dotenv(".env")

# ── Baca konfigurasi TokenRouter dari .env ──────────────────────────────────
BASE_URL = os.getenv("TOKENROUTER_BASE_URL", "https://api.tokenrouter.com/v1")
API_KEY  = os.getenv("TOKENROUTER_API_KEY")
MODEL    = os.getenv("TOKENROUTER_MODEL",    "MiniMax-M3")

if not API_KEY or API_KEY == "sk-tokenrouter-xxx":
    raise EnvironmentError(
        "❌ TOKENROUTER_API_KEY tidak ditemukan atau belum diisi di .env! "
        "Pastikan sudah mengisi TOKENROUTER_API_KEY=<api-key-anda>"
    )


def main():
    input_file  = "scenario1_data.json"
    output_file = "answers.json"

    # 1. Baca data sumber (Skenario 1)
    if not os.path.exists(input_file):
        print(
            f"❌ Error: File {input_file} tidak ditemukan. "
            "Jalankan task1 terlebih dahulu."
        )
        return

    with open(input_file, "r", encoding="utf-8") as f:
        source_data = json.load(f)

    # 2. Fitur Resume: baca hasil yang sudah pernah dikerjakan
    results       = []
    processed_ids = set()

    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                results = json.load(f)
                for r in results:
                    if r.get("actual_output"):
                        processed_ids.add(r["query_id"])
            except json.JSONDecodeError:
                print("⚠️  File answers.json korup atau kosong, membuat daftar baru...")
                results = []

    print(
        f"🔄 Fitur Resume Aktif: Ditemukan {len(processed_ids)} soal yang sudah terjawab sebelumnya."
    )
    print(f"🤖 Model   : {MODEL}")
    print(f"🌐 Base URL: {BASE_URL}")

    # 3. Inisialisasi client TokenRouter
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
    )

    print(f"\n🚀 Mulai generate jawaban dengan TokenRouter ({MODEL})...\n")

    limit_per_run         = 30  # Maks 30 soal per run
    processed_in_this_run = 0

    for item in source_data:
        if item["query_id"] in processed_ids:
            continue  # Lewati yang sudah dikerjakan

        if processed_in_this_run >= limit_per_run:
            print(
                f"\n⏸️  Telah mencapai batas eksekusi ({limit_per_run} soal) pada sesi ini."
            )
            print(
                "Silakan tunggu sebentar, lalu jalankan ulang script ini untuk melanjutkan!"
            )
            break

        print(f"⏳ Memproses Soal ID: {item['query_id']} ...")
        try:
            # Menggunakan stream sesuai dokumentasi / contoh
            start_time = time.time()
            stream = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Anda adalah asisten AI yang bertugas menjawab pertanyaan SPBE "
                            "secara akurat, singkat, dan jelas berdasarkan pengetahuan yang Anda miliki."
                        ),
                    },
                    {"role": "user", "content": item["query"]},
                ],
                stream=True,
                stream_options={"include_usage": True},
                extra_body={}
            )

            content_parts = []
            for chunk in stream:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        content_parts.append(delta.content)

            actual_output = "".join(content_parts)
            end_time = time.time()
            response_time = round(end_time - start_time, 2)

        except Exception as e:
            print(f"❌ Error API saat memproses query ID {item['query_id']}: {e}")
            print(
                "🛑 Memberhentikan eksekusi sementara. Silakan coba lagi nanti."
            )
            break

        # Simpan jawaban ke item
        item["actual_output"] = actual_output
        item["response_time_seconds"] = response_time

        # Update jika sudah ada, atau append baru
        updated = False
        for i, existing in enumerate(results):
            if existing["query_id"] == item["query_id"]:
                results[i] = item
                updated = True
                break
        if not updated:
            results.append(item)

        processed_ids.add(item["query_id"])
        processed_in_this_run += 1

        # Auto-save setiap selesai 1 soal
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        # Jeda 1 detik antar request
        time.sleep(1)

    print(
        f"\n✅ Selesai sesi ini. Total progres: {len(processed_ids)}/{len(source_data)} soal terjawab."
    )
    if len(processed_ids) < len(source_data):
        print("💡 Ketik ulang `python task2_run_tokenrouter.py` untuk melanjutkan sisa soal!")


if __name__ == "__main__":
    main()
