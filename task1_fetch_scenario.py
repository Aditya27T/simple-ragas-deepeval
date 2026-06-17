import json
import openpyxl

def main():
    # Path ke file excel dataset (sesuaikan jika berbeda)
    excel_path = "../dataset_maja_ai.xlsx"
    print(f"Membaca dataset dari {excel_path}...")
    
    # Buka workbook
    wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
    ws = wb["Skenario 1"]
    
    data = []
    # Baris 2 sampai 101 adalah 100 data pertama
    for i, row in enumerate(ws.iter_rows(min_row=2, max_row=101, values_only=True)):
        if not row[1]:  # Skip jika query kosong
            continue
            
        item = {
            "query_id": row[0],
            "query": str(row[1]).strip() if row[1] else "",
            "query_type": str(row[2]).strip() if row[2] else "",
            "expected_output": str(row[3]).strip() if row[3] else "",
            "source": str(row[4]).strip() if row[4] else ""
        }
        data.append(item)
    
    output_file = "scenario1_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Berhasil mengambil {len(data)} skenario dan disimpan ke {output_file}")

if __name__ == "__main__":
    main()
