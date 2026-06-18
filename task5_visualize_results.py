import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    # 1. Load data
    file_path = 'evaluation_results_deepeval_only.json'
    if not os.path.exists(file_path):
        print(f"File {file_path} tidak ditemukan!")
        return
        
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. Ekstrak data yang dibutuhkan
    rows = []
    for item in data:
        evals = item.get('evaluations', {})
        row = {
            'query_id': item.get('query_id'),
            'query_type': item.get('query_type', 'Uncategorized'),
            'deepeval_hallucination': evals.get('deepeval_hallucination'),
            'deepeval_geval_correctness': evals.get('deepeval_geval_correctness'),
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # 3. Buat folder untuk menyimpan hasil gambar grafik
    out_dir = 'visualizations'
    os.makedirs(out_dir, exist_ok=True)

    # Set tema grafik yang bersih
    sns.set_theme(style="whitegrid")

    print("Mulai membuat visualisasi data...")

    # --- Plot 1: Bar Chart Rata-rata Skor ---
    plt.figure(figsize=(8, 6))
    avg_scores = df[['deepeval_geval_correctness', 'deepeval_hallucination']].mean()
    sns.barplot(x=avg_scores.index, y=avg_scores.values, palette='viridis')
    plt.title('Rata-Rata Skor Metrik Keseluruhan', fontsize=14)
    plt.ylabel('Skor (0 - 1)', fontsize=12)
    plt.ylim(0, 1.1)
    # Tambahkan label angka di atas batang grafik
    for index, value in enumerate(avg_scores.values):
        plt.text(index, value + 0.02, f'{value:.2f}', ha='center', fontsize=12)
    plt.savefig(f'{out_dir}/1_rata_rata_skor.png', dpi=300, bbox_inches='tight')
    plt.close()

    # --- Plot 2: Bar Chart Rata-rata Berdasarkan Query Type ---
    if df['query_type'].nunique() > 1:
        plt.figure(figsize=(10, 6))
        df_melted = df.melt(id_vars=['query_type'], 
                            value_vars=['deepeval_geval_correctness', 'deepeval_hallucination'], 
                            var_name='Metric', value_name='Score')
        
        sns.barplot(data=df_melted, x='query_type', y='Score', hue='Metric', palette='muted')
        plt.title('Skor DeepEval Berdasarkan Tipe Pertanyaan (Query Type)', fontsize=14)
        plt.ylabel('Rata-rata Skor (0 - 1)')
        plt.ylim(0, 1.1)
        plt.xticks(rotation=45, ha='right') # Memutar label agar tidak bertumpuk
        plt.legend(title='Metric')
        plt.tight_layout() # Menyesuaikan margin agar label tidak terpotong
        plt.savefig(f'{out_dir}/2_skor_per_kategori.png', dpi=300, bbox_inches='tight')
        plt.close()

    # --- Plot 3: Distribusi/Histogram Skor Correctness ---
    plt.figure(figsize=(8, 6))
    sns.histplot(data=df, x='deepeval_geval_correctness', bins=10, kde=True, color='blue')
    plt.title('Distribusi Nilai Correctness', fontsize=14)
    plt.xlabel('Skor Correctness (0 - 1)')
    plt.ylabel('Frekuensi')
    plt.savefig(f'{out_dir}/3_distribusi_correctness.png', dpi=300, bbox_inches='tight')
    plt.close()

    # --- Ekspor ke CSV / Excel Format ---
    csv_path = f'{out_dir}/evaluation_summary.csv'
    df.to_csv(csv_path, index=False)
    
    print(f"Visualisasi selesai! Grafik gambar (.png) dan data rekap (.csv) telah disimpan di folder '{out_dir}/'.")

if __name__ == "__main__":
    main()
