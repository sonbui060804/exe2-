import csv
import json
from pathlib import Path
from database import get_db

BASE_DIR = Path(r"d:\exe2\ai_invoice_dataset")
EXPORTS_DIR = BASE_DIR / "exports"
MISA_DIR = EXPORTS_DIR / "misa"
FAST_DIR = EXPORTS_DIR / "fast"
EXCEL_DIR = EXPORTS_DIR / "excel"
TRAIN_DIR = EXPORTS_DIR / "training"

def export_all():
    db = get_db()
    # Lấy hóa đơn (có thể lọc trạng thái APPROVED, ở đây lấy hết để test)
    invoices = list(db.invoices.find({}))
    if not invoices:
        print("No invoices to export.")
        return

    print(f"Start exporting {len(invoices)} invoices...")

    # 1. EXCEL SUMMARY
    excel_path = EXCEL_DIR / "invoice_summary.csv"
    with open(excel_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["ID Hóa Đơn", "Số HĐ", "Ngày Lập", "MST Người Bán", "Tên Người Bán", "Tổng Tiền Hàng", "Tiền Thuế", "Tổng Thanh Toán"])
        for inv in invoices:
            info = inv.get("invoice_info", {})
            seller = inv.get("seller_info", {})
            totals = inv.get("totals", {})
            writer.writerow([
                inv.get("document_id", ""),
                info.get("invoice_no", ""),
                info.get("issue_date", ""),
                seller.get("tax_code", ""),
                seller.get("legal_name", ""),
                totals.get("total_amount_before_tax", 0),
                totals.get("total_tax_amount", 0),
                totals.get("total_amount_after_tax", 0)
            ])
    print(f" -> Exported Excel: {excel_path}")

    # 2. FAST ERP IMPORT FORMAT
    fast_path = FAST_DIR / "fast_import.csv"
    with open(fast_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["So_Ct", "Ngay_Ct", "Ma_Kh", "Ten_Kh", "Ma_Vt", "So_Luong", "Gia", "Tien", "Thue"])
        for inv in invoices:
            doc_id = inv.get("document_id", "")
            date = inv.get("invoice_info", {}).get("issue_date", "")
            buyer_tax = inv.get("buyer_info", {}).get("tax_code", "")
            buyer_name = inv.get("buyer_info", {}).get("legal_name", "")
            
            items = inv.get("items", [])
            for item in items:
                writer.writerow([
                    doc_id, date, buyer_tax, buyer_name,
                    item.get("item_name", "HH"),
                    item.get("quantity", 1),
                    item.get("unit_price", 0),
                    item.get("amount_before_tax", 0),
                    item.get("tax_amount", 0)
                ])
    print(f" -> Exported FAST: {fast_path}")

    # 3. MISA ERP XML FORMAT (Mockup cấu trúc)
    misa_path = MISA_DIR / "misa_import.xml"
    with open(misa_path, 'w', encoding='utf-8') as f:
        f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        f.write("<Invoices>\n")
        for inv in invoices:
            f.write("  <Invoice>\n")
            f.write(f"    <InvNo>{inv.get('invoice_info', {}).get('invoice_no', '')}</InvNo>\n")
            f.write(f"    <Total>{inv.get('totals', {}).get('total_amount_after_tax', 0)}</Total>\n")
            f.write("  </Invoice>\n")
        f.write("</Invoices>\n")
    print(f" -> Exported MISA: {misa_path}")

    # 4. TRAINING JSONL
    train_path = TRAIN_DIR / "qwen_finetune.jsonl"
    with open(train_path, 'w', encoding='utf-8') as f:
        for inv in invoices:
            doc_id = inv.get("document_id")
            
            # Xóa các metadata không cần thiết trước khi làm output chuẩn
            clean_inv = {k:v for k,v in inv.items() if k not in ["_id", "workflow", "ai_metadata"]}
            
            record = {
                "instruction": "Trích xuất thông tin hóa đơn này thành JSON",
                "input": f"[Dữ liệu OCR thô của {doc_id} sẽ được gép vào đây từ PaddleOCR]",
                "output": json.dumps(clean_inv, ensure_ascii=False)
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f" -> Exported Training Data: {train_path}")

if __name__ == "__main__":
    export_all()
