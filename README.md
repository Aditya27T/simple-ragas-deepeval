# Simple RAGAS & DeepEval Evaluator

Repository ini berisi sekumpulan skrip Python mandiri yang dirancang untuk melakukan proses evaluasi model LLM secara bertahap. Sistem ini dibangun dengan fokus pada pencegahan *API rate limit*, dan dilengkapi dengan fitur auto-resume agar sangat mudah digunakan pada *environment* berskala kecil.

## ⚙️ Persiapan & Instalasi

1. **Pastikan Anda berada di dalam folder proyek ini:**
   ```bash
   cd /Users/adityarahmadani/Documents/UM/PI/LLM_EVAL/simple_tasks
   ```

2. **Buat file `.env` dari *template* yang disediakan:**
   Salin file `.env.example` menjadi `.env`, lalu masukkan API Key OpenRouter Anda.
   ```bash
   cp .env.example .env
   ```
   Buka file `.env` dan atur isinya:
   ```ini
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxx
   JUDGE_MODEL=anthropic/claude-3.5-sonnet
   ```

3. **Install Dependencies:**
   Install semua *library* yang dibutuhkan menggunakan file `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🐳 Menjalankan dengan Docker

Cara termudah menjalankan tanpa perlu install Python/dependencies di lokal.

### Prasyarat
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/) sudah terinstall
- File `.env` sudah dibuat (lihat langkah **Persiapan** di atas)
- File `dataset_maja_ai.xlsx` diletakkan **satu direktori di atas** folder proyek ini (atau sesuaikan path di `task1_fetch_scenario.py`)

### 1. Build Docker Image
```bash
docker compose build
```

### 2. Jalankan Setiap Task Secara Berurutan

**Tugas 1** – Ekstrak dataset dari Excel:
```bash
docker compose run --rm task1
```

**Tugas 2** – Generate jawaban via LLM (ulangi hingga semua 100 soal selesai):
```bash
docker compose run --rm task2
```

**Tugas 3** – Evaluasi hasil dengan RAGAS & DeepEval (ulangi hingga semua soal terevaluasi):
```bash
docker compose run --rm task3
```

**Tugas 4** – Evaluasi hasil dengan DeepEval saja (tanpa RAGAS) (opsional, jika tidak ingin pakai Task 3):
```bash
docker compose run --rm task4
```

> **💡 Tips:** Semua file output (`scenario1_data.json`, `answers.json`, `evaluation_results.json`, `evaluation_results_deepeval_only.json`) akan tersimpan langsung di direktori proyek Anda (bukan di dalam container), sehingga progres aman meski container dihapus.

---

## 🔧 Tutorial: Menggunakan DeepSeek / Minimax Langsung (Tanpa OpenRouter)

Secara bawaan, **Tugas 2** menggunakan API OpenRouter. Jika Anda memiliki API Key langsung dari DeepSeek atau Minimax, Anda bisa menggunakannya tanpa perlu mengubah kode Python-nya.

Buka file `.env` Anda, lalu cari bagian "TUGAS 2" dan hilangkan tanda pagar (`#`) pada model yang ingin Anda gunakan.

**Contoh jika ingin memakai DeepSeek:**
```ini
TEST_BASE_URL=https://api.deepseek.com/v1
TEST_API_KEY=sk-deepseek-xxx
TEST_MODEL=deepseek-chat
```
*(Catatan: Biarkan bagian Tugas 3 / Juri tetap memakai OpenRouter)*

---

## 🚀 Cara Menjalankan (Tanpa Docker)

Proses dibagi menjadi 3 tahapan (tugas) yang **harus dijalankan secara berurutan**.

### 📌 Tugas 1: Ekstrak Dataset (Skenario 1)
Skrip ini akan mengambil 100 data uji dari file excel sumber.
- **Perintah:**
  ```bash
  python task1_fetch_scenario.py
  ```
- **Fungsi:** Membaca file `dataset_maja_ai.xlsx` dan menyimpan format JSON ke `scenario1_data.json`.

### 📌 Tugas 2: Generate Jawaban via LLM (OpenRouter)
Skrip ini akan bertindak sebagai asisten AI yang menjawab pertanyaan di dataset.
- **Perintah:**
  ```bash
  python task2_run_openrouter.py
  ```
- **Fitur Spesial:** Skrip ini memiliki batasan pemrosesan maksimal 30 pertanyaan per eksekusi untuk menghindari batas *limit* OpenRouter. Data akan otomatis di-*save* setiap selesai 1 soal ke `answers.json`.
- **Cara Melanjutkan:** Saat skrip berhenti, cukup ketik kembali perintah di atas. Ia akan **otomatis lanjut** ke soal berikutnya yang belum dikerjakan. Ulangi terus hingga semua 100 soal selesai.

### 📌 Tugas 3: Evaluasi Hasil Menggunakan Judge Model (RAGAS & DeepEval)
Skrip ini bertindak sebagai juri penilai otomatis terhadap jawaban AI.
- **Perintah:**
  ```bash
  python task3_evaluate.py
  ```
- **Fitur Spesial:** Sama dengan Tugas 2, skrip ini hanya mengevaluasi batch 30 jawaban setiap kali dijalankan untuk menghindari terkurasnya saldo API Judge Model. Hasil setiap evaluasi RAGAS dan DeepEval akan langsung disimpan secara aman di `evaluation_results.json`.
- **Cara Melanjutkan:** Jalankan kembali perintah secara berulang hingga semua pertanyaan mendapatkan skor evaluasinya.

### 📌 Tugas 4: Evaluasi Hasil Menggunakan DeepEval Saja
Skrip ini berfungsi sama dengan Tugas 3, tetapi *hanya* menjalankan evaluasi menggunakan DeepEval (tanpa memanggil API RAGAS). Ini berguna jika Anda mengalami kendala pada *rate limit* RAGAS atau ingin fokus pada metrik DeepEval.
- **Perintah:**
  ```bash
  python task4_evaluate_deepeval_only.py
  ```
- **Fitur Spesial:** Menggunakan `answers.json` dan menyimpan hasil ke file terpisah bernama `evaluation_results_deepeval_only.json` agar tidak tertukar dengan hasil Tugas 3.
- **Cara Melanjutkan:** Jalankan kembali perintah secara berulang hingga selesai.
