import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any

# Thêm đường dẫn tới thư mục scripts để dùng chung hàm database
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.append(str(scripts_dir))

from database import get_db

BASE_DIR = Path(r"d:\exe2\ai_invoice_dataset")

app = FastAPI(title="AI-Invoice Backend", version="1.0")

# Cấu hình CORS để Frontend (React/Vite chạy ở port 5173) có thể gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phục vụ thư mục chứa ảnh gốc để UI hiển thị được
images_dir = BASE_DIR / "invoices" / "processed"
if images_dir.exists():
    app.mount("/static", StaticFiles(directory=str(images_dir)), name="static")


@app.get("/api/invoices")
def get_invoices():
    db = get_db()
    cursor = db.invoices.find({}, {"_id": 0, "items": 0})
    invoices = list(cursor)
    return {"invoices": invoices}

@app.get("/api/invoices/{doc_id}")
def get_invoice_detail(doc_id: str):
    db = get_db()
    invoice = db.invoices.find_one({"document_id": doc_id}, {"_id": 0})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"invoice": invoice}

class ApproveRequest(BaseModel):
    data: Dict[str, Any]

@app.post("/api/invoices/{doc_id}/approve")
def approve_invoice(doc_id: str, payload: ApproveRequest):
    db = get_db()
    invoice = db.invoices.find_one({"document_id": doc_id})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
        
    updated_data = payload.data
    if "workflow" not in updated_data:
        updated_data["workflow"] = {}
    updated_data["workflow"]["status"] = "APPROVED"
    
    db.invoices.update_one(
        {"document_id": doc_id},
        {"$set": updated_data}
    )
    return {"message": "Duyệt thành công", "document_id": doc_id}

# --- AUTH & SAAS FEATURES ---
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/login")
def login(payload: LoginRequest):
    # Mock tài khoản cho Gói Freemium
    if payload.username == "admin" and payload.password == "123456":
        return {"token": "fake-jwt-token-admin", "user": {"username": "admin", "role": "admin"}}
    raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")

@app.post("/api/upload")
def upload_invoices():
    db = get_db()
    # Check Quota Gài Bẫy (Lock-in)
    count = db.invoices.count_documents({})
    if count >= 50:
        raise HTTPException(status_code=403, detail="Tài khoản đã hết Quota miễn phí (50/50). Vui lòng nâng cấp gói SaaS hoặc On-Premise!")
    return {"message": "Upload thành công vào hàng đợi AI"}

