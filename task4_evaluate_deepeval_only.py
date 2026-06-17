import json
import os
import time

# DeepEval
from deepeval.metrics import GEval, HallucinationMetric
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load konfigurasi API Key
load_dotenv(".env")
os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"


# --- Setup OpenRouter untuk Judge / Evaluator ---
class OpenRouterJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.model = ChatOpenAI(
            model=os.getenv("JUDGE_MODEL", "openai/gpt-4o-mini"),
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0,
            max_tokens=1000,
        )

    def load_model(self):
        return self.model

    def generate(self, prompt: str) -> str:
        return self.model.invoke(prompt).content

    async def a_generate(self, prompt: str) -> str:
        return (await self.model.ainvoke(prompt)).content

    def get_model_name(self) -> str:
        return os.getenv("JUDGE_MODEL", "openai/gpt-4o-mini")


def main():
    input_file = "answers.json"
    output_file = "evaluation_results_deepeval_only.json"

    if not os.path.exists(input_file):
        print(
            f"❌ Error: File {input_file} tidak ditemukan. Jalankan task2 terlebih dahulu."
        )
        return

    # 1. Baca data sumber (yang sudah ada jawabannya)
    with open(input_file, "r", encoding="utf-8") as f:
        source_data = json.load(f)

    # 2. Fitur Resume: Cek hasil evaluasi sebelumnya
    evaluated_results = []
    processed_ids = set()

    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                evaluated_results = json.load(f)
                for r in evaluated_results:
                    # Jika data ini sudah memiliki nilai "evaluations", masukkan ke set
                    if "evaluations" in r:
                        processed_ids.add(r["query_id"])
            except json.JSONDecodeError:
                print(f"⚠️ File {output_file} korup/kosong. Membuat baru...")
                evaluated_results = []

    print(
        f"🔄 Fitur Resume Aktif: Ditemukan {len(processed_ids)} soal yang sudah selesai dievaluasi."
    )

    # Kumpulkan hanya soal-soal yang belum dievaluasi
    pending_items = [
        item for item in source_data if item["query_id"] not in processed_ids
    ]

    if not pending_items:
        print("✅ Semua jawaban telah dievaluasi!")
        return

    # Ambil maksimal 30 soal per sesi untuk menghindari limit OpenRouter
    limit_per_run = 30
    batch_items = pending_items[:limit_per_run]
    print(f"\n⏳ Memulai evaluasi (DeepEval saja) untuk {len(batch_items)} soal pada sesi ini...")

    # --- SETUP LLM ---
    api_key = os.getenv("OPENROUTER_API_KEY")
    os.environ["OPENAI_API_KEY"] = api_key
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

    judge = OpenRouterJudge()
    hallucination_metric = HallucinationMetric(
        threshold=0.3, model=judge, include_reason=False
    )
    geval_metric = GEval(
        name="Correctness",
        model=judge,
        criteria="Periksa apakah jawaban AI (actual_output) sesuai dengan referensi (expected_output).",
        evaluation_params=[
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
        threshold=0.7,
    )

    # ---------------------------------------------------------
    # 3. EVALUASI DEEPEVAL & AUTO-SAVE
    # ---------------------------------------------------------
    print("\n--- 🔬 Memulai Evaluasi DeepEval & Auto-Save ---")

    for i, item in enumerate(batch_items):
        print(f"   Mengevaluasi DeepEval untuk ID {item['query_id']} ...")

        tc = LLMTestCase(
            input=item["query"],
            actual_output=item.get("actual_output", ""),
            expected_output=item.get("expected_output", ""),
            context=[item.get("source", "(tidak ada)")],
        )

        # Ukur Hallucination
        try:
            hallucination_metric.measure(tc)
            hal_score = hallucination_metric.score
        except Exception as e:
            print(f"      ⚠️ Hallucination error pada index {i}: {e}")
            hal_score = 0.0

        # Ukur GEval
        try:
            geval_metric.measure(tc)
            geval_score = geval_metric.score
        except Exception as e:
            print(f"      ⚠️ GEval error pada index {i}: {e}")
            geval_score = 0.0

        # Simpan DeepEval saja
        item["evaluations"] = {
            "deepeval_hallucination": float(hal_score),
            "deepeval_geval_correctness": float(geval_score),
        }

        # Tambahkan ke daftar master (update jika sudah ada, atau append)
        updated_existing = False
        for j, existing_item in enumerate(evaluated_results):
            if existing_item["query_id"] == item["query_id"]:
                evaluated_results[j] = item
                updated_existing = True
                break

        if not updated_existing:
            evaluated_results.append(item)

        # AUTO-SAVE PER SOAL
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(evaluated_results, f, indent=4, ensure_ascii=False)

        time.sleep(1)  # Jeda agar aman dari limit

    print(
        f"\n✅ Selesai sesi ini. Total progres evaluasi: {len(evaluated_results)}/{len(source_data)} soal."
    )
    if len(evaluated_results) < len(source_data):
        print(
            "💡 Ketik ulang `python task4_evaluate_deepeval_only.py` untuk melanjutkan evaluasi sisa soal!"
        )


if __name__ == "__main__":
    main()
