import pymongo
from pymongo import MongoClient

# Cấu hình kết nối MongoDB
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "ai_invoice_db"

def get_db():
    """Tạo kết nối tới MongoDB và trả về object database."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Lệnh dưới đây sẽ throw exception nếu không kết nối được
    client.server_info()
    return client[DB_NAME]

def get_company_by_tax_code(tax_code):
    db = get_db()
    company = db.companies.find_one({"tax_code": tax_code})
    return company

def save_invoice(doc_id, invoice_data):
    db = get_db()
    # Upsert (Update if exists, else Insert)
    db.invoices.update_one(
        {"document_id": doc_id},
        {"$set": invoice_data},
        upsert=True
    )
    return True

if __name__ == "__main__":
    print("Testing MongoDB Connection...")
    try:
        db = get_db()
        print(f"[OK] Successfully connected to MongoDB database: '{DB_NAME}'")
        # In ra số lượng collection hiện tại
        collections = db.list_collection_names()
        print(f"Collections present: {collections}")
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(f"[FAILED] Could not connect to MongoDB at {MONGO_URI}.")
        print("Lỗi chi tiết:", err)
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
