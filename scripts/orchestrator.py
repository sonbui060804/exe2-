import os
import shutil
import json
from pathlib import Path
from database import get_db, save_invoice

BASE_DIR = Path(r"d:\exe2\ai_invoice_dataset")
RAW_DIR = BASE_DIR / "invoices" / "raw"
PROCESSED_DIR = BASE_DIR / "invoices" / "processed"
FAILED_DIR = BASE_DIR / "invoices" / "failed"
GT_DIR = BASE_DIR / "ground_truth"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FAILED_DIR.mkdir(parents=True, exist_ok=True)

def run_pipeline():
    print("Starting AI Orchestrator Pipeline (Local Mode)...")
    db = get_db()
    
    # Đếm số lượng hóa đơn đã xử lý để chặn nếu quá 50 (Gài bẫy Freemium)
    total_processed = db.invoices.count_documents({})
    QUOTA_LIMIT = 50
    
    raw_files = list(RAW_DIR.glob("*.png")) + list(RAW_DIR.glob("*.jpg"))
    if not raw_files:
        print("No raw invoices found in queue.")
        return

    print(f"Found {len(raw_files)} invoices to process.")
    
    processed_count = 0
    
    for img_path in raw_files:
        if total_processed >= QUOTA_LIMIT:
            print(f"⚠️ QUOTA REACHED ({QUOTA_LIMIT}/{QUOTA_LIMIT}). System locked for new processing.")
            break
            
        doc_id = img_path.stem
        print(f"Processing {doc_id}...")
        
        # Mô phỏng AI đọc xong và lấy kết quả từ Ground Truth
        gt_path = GT_DIR / f"{doc_id}.json"
        
        if gt_path.exists():
            with open(gt_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Gắn thêm trạng thái PENDING_REVIEW chờ kế toán duyệt
            data["workflow"] = {
                "status": "PENDING_REVIEW"
            }
            data["ai_metadata"] = {
                "overall_confidence": 0.95
            }
            
            # Cấu trúc items (vì ground truth ban đầu chưa có mảng items chi tiết, ta fake 1 tí)
            if "totals" in data and "total_amount_before_tax" in data["totals"]:
                data["items"] = [
                    {
                        "item_name": "Sản phẩm / Dịch vụ bóc tách",
                        "quantity": 1,
                        "unit_price": data["totals"]["total_amount_before_tax"],
                        "amount_before_tax": data["totals"]["total_amount_before_tax"]
                    }
                ]
            
            # Lưu vào MongoDB
            save_invoice(doc_id, data)
            
            # Move file ảnh sang thư mục processed
            dest_path = PROCESSED_DIR / img_path.name
            shutil.move(str(img_path), str(dest_path))
            print(f"  -> [SUCCESS] Moved to processed. DB Updated.")
            
            processed_count += 1
            total_processed += 1
        else:
            # Nếu lỗi (không có ground truth), move sang failed
            dest_path = FAILED_DIR / img_path.name
            shutil.move(str(img_path), str(dest_path))
            print(f"  -> [FAILED] Moved to failed.")
            
    print(f"\nPipeline finished. Processed {processed_count} invoices.")
    print(f"Current Quota Usage: {total_processed} / {QUOTA_LIMIT}")

if __name__ == "__main__":
    run_pipeline()
