# Simple Tasks Pipeline

Direktori ini berisi 3 script Python mandiri (tanpa pipeline OOP yang rumit) agar mudah dibagi menjadi 3 tugas terpisah:

## Tugas 1: Ekstrak Dataset (Skenario 1)
**File**: `task1_fetch_scenario.py`
- Membaca file `dataset_maja_ai.xlsx`
- Mengambil 100 data dari "Skenario 1"
- Menyimpan hasilnya dalam format JSON (`scenario1_data.json`)
- **Cara Jalan**: `python task1_fetch_scenario.py`

## Tugas 2: Integrasi OpenRouter (LLM)
**File**: `task2_run_openrouter.py`
- Membaca file `scenario1_data.json` dari Tugas 1
- Meminta jawaban dari model LLM melalui API OpenRouter.
- Menyimpan hasil beserta jawaban asli ke dalam `answers.json`
- **Cara Jalan**: `python task2_run_openrouter.py`

## Tugas 3: Evaluasi RAGAS & DeepEval
**File**: `task3_evaluate.py`
- Membaca file `answers.json` dari Tugas 2
- Melakukan perhitungan skor RAGAS (Answer Relevancy, Faithfulness, Correctness)
- Melakukan perhitungan skor DeepEval (Hallucination, GEval Correctness)
- Menyimpan hasil akhir beserta skor evaluasi ke dalam `evaluation_results.json`
- **Cara Jalan**: `python task3_evaluate.py`

### Persyaratan:
1. Pastikan file `.env` di folder utama (`project1_llm_eval/.env`) memiliki nilai `OPENROUTER_API_KEY`.
2. Pastikan dependencies diinstal (`pip install openpyxl openai deepeval ragas datasets python-dotenv langchain-openai`).
