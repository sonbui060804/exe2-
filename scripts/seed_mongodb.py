import json
from pathlib import Path
import pymongo
from database import get_db

def seed_database():
    db = get_db()
    
    base_dir = Path(r"d:\exe2\ai_invoice_dataset")
    master_db_path = base_dir / "data" / "master_db.json"
    gt_dir = base_dir / "ground_truth"
    
    # 1. Setup Indexes
    print("Setting up indexes...")
    db.companies.create_index([("tax_code", pymongo.ASCENDING)], unique=True)
    db.invoices.create_index([("document_id", pymongo.ASCENDING)], unique=True)
    
    # 2. Seed Companies
    print(f"Seeding companies from {master_db_path.name}...")
    if master_db_path.exists():
        with open(master_db_path, "r", encoding="utf-8") as f:
            master_data = json.load(f)
            
        companies_to_insert = []
        for tax_code, info in master_data.items():
            company_doc = {
                "tax_code": tax_code,
                "legal_name": info.get("legal_name", ""),
                "address": info.get("address", "")
            }
            companies_to_insert.append(company_doc)
            
        if companies_to_insert:
            # Upsert companies
            for doc in companies_to_insert:
                db.companies.update_one(
                    {"tax_code": doc["tax_code"]},
                    {"$set": doc},
                    upsert=True
                )
            print(f"  -> Upserted {len(companies_to_insert)} companies.")
    else:
        print("  -> master_db.json not found!")
        
    # 3. Seed Invoices (Ground Truth data)
    print(f"Seeding invoices from {gt_dir.name}...")
    gt_files = list(gt_dir.glob("*.json"))
    invoices_inserted = 0
    for gt_file in gt_files:
        with open(gt_file, "r", encoding="utf-8") as f:
            gt_data = json.load(f)
            
        doc_id = gt_file.stem
        # Bổ sung document_id và status
        gt_data["document_id"] = doc_id
        gt_data["workflow"] = {"status": "VERIFIED"}
        
        db.invoices.update_one(
            {"document_id": doc_id},
            {"$set": gt_data},
            upsert=True
        )
        invoices_inserted += 1
        
    print(f"  -> Upserted {invoices_inserted} ground truth invoices.")
    print("\nDatabase Seeding Completed Successfully!")

if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"Error seeding database: {e}")
