import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

# Load API Key dari .env
load_dotenv(".env")


def main():
    input_file = "scenario1_data.json"
    output_file = "answers1.json"

    # 1. Baca data sumber (Skenario 1)
    if not os.path.exists(input_file):
        print(
            f"❌ Error: File {input_file} tidak ditemukan. Jalankan task1 terlebih dahulu."
        )
        return

    with open(input_file, "r", encoding="utf-8") as f:
        source_data = json.load(f)

    # 2. Baca data yang sudah pernah dikerjakan (Fitur Resume)
    results = []
    processed_ids = set()

    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                results = json.load(f)
                # Catat ID yang sudah memiliki jawaban berhasil
                for r in results:
                    if r.get("actual_output"):
                        processed_ids.add(r["query_id"])
            except json.JSONDecodeError:
                print("⚠️ File answers.json korup atau kosong, membuat daftar baru...")
                results = []

    print(
        f"🔄 Fitur Resume Aktif: Ditemukan {len(processed_ids)} soal yang sudah terjawab sebelumnya."
    )

    # Inisialisasi client OpenRouter
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    model_name = "google/gemma-4-31b-it:free"
    print(f"🚀 Mulai generate jawaban dengan model: {model_name}...")

    limit_per_run = 30  # Batasi eksekusi maksimal 30 soal per run
    processed_in_this_run = 0

    for idx, item in enumerate(source_data):
        if item["query_id"] in processed_ids:
            continue  # Lewati yang sudah dikerjakan

        if processed_in_this_run >= limit_per_run:
            print(
                f"\n⏸️ Telah mencapai batas eksekusi ({limit_per_run} soal) pada sesi ini untuk menghindari limit OpenRouter."
            )
            print(
                "Silakan tunggu sebentar, lalu jalankan ulang script ini untuk melanjutkan sisa soal berikutnya!"
            )
            break

        print(f"⏳ Memproses Soal ID: {item['query_id']} ...")
        try:
            start_time = time.time()
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "Anda adalah asisten AI yang bertugas menjawab pertanyaan SPBE secara akurat, singkat, dan jelas berdasarkan pengetahuan yang Anda miliki.",
                    },
                    {"role": "user", "content": item["query"]},
                ],
                temperature=0.0,
                max_tokens=1000,
            )
            actual_output = response.choices[0].message.content
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
        except Exception as e:
            print(f"❌ Error API saat memproses query ID {item['query_id']}: {e}")
            print(
                "🛑 Memberhentikan eksekusi sementara (kemungkinan limit tercapai). Silakan coba lagi nanti."
            )
            break

        # Simpan hasil jawaban ke item
        item["actual_output"] = actual_output
        item["response_time_seconds"] = response_time

        # Cari apakah item ini sebelumnya ada tapi gagal, lalu update. Jika tidak, tambahkan baru.
        updated_existing = False
        for i, existing_item in enumerate(results):
            if existing_item["query_id"] == item["query_id"]:
                results[i] = item
                updated_existing = True
                break

        if not updated_existing:
            results.append(item)

        processed_ids.add(item["query_id"])
        processed_in_this_run += 1

        # 3. Langsung simpan ke disk SETIAP KALI SELESAI 1 SOAL
        # (Sehingga aman jika script mati tiba-tiba, progres tidak hilang)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

        # Beri jeda 2 detik per soal agar lebih stabil dan tidak spammy ke API
        time.sleep(2)

    print(
        f"\n✅ Selesai sesi ini. Total keseluruhan progres: {len(processed_ids)}/{len(source_data)} soal terjawab."
    )
    if len(processed_ids) < len(source_data):
        print(
            "💡 Ketik ulang `python task2_run_openrouter.py` untuk melanjutkan sisa soal!"
        )


if __name__ == "__main__":
    main()
