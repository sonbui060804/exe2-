import json
from pathlib import Path

def build_master_db():
    base_dir = Path(r"d:\exe2\ai_invoice_dataset")
    gt_dir = base_dir / "ground_truth"
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    master_db = {}
    
    for gt_file in gt_dir.glob("*.json"):
        with open(gt_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        seller = data.get("seller_info", {})
        if seller.get("tax_code"):
            master_db[seller["tax_code"]] = {
                "legal_name": seller.get("legal_name", ""),
                "address": seller.get("address", "")
            }
            
        buyer = data.get("buyer_info", {})
        if buyer.get("tax_code"):
            master_db[buyer["tax_code"]] = {
                "legal_name": buyer.get("legal_name", ""),
                "address": buyer.get("address", "")
            }
            
    db_path = data_dir / "master_db.json"
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(master_db, f, ensure_ascii=False, indent=2)
        
    print(f"Master DB built with {len(master_db)} companies at {db_path}")

if __name__ == "__main__":
    build_master_db()
