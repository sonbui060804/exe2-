import json
import requests
from pathlib import Path
import sys
import time
import concurrent.futures
from regex_engine import extract_hard_fields
from bbox_utils import cluster_and_format_markdown
from validators import run_validation_engine
from database import get_company_by_tax_code, save_invoice

# Directories
BASE_DIR = Path(r"d:\exe2\ai_invoice_dataset")
OCR_DIR = BASE_DIR / "ocr" / "paddleocr"
OUTPUT_DIR = BASE_DIR / "llm_predictions" / "qwen25"
PROMPT_FILE = BASE_DIR / "schemas" / "qwen25_prompt_v4.txt"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load Prompt Template
with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompt_template = f.read()

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

def merge_results(llm_data, regex_data):
    """
    Merge Engine V4: 
    - Hard Fields lấy từ Regex.
    - Seller/Buyer Info lấy từ MongoDB (tra cứu bằng Tax Code).
    - Items lấy từ LLM.
    """
    # 1. Ép cứng dữ liệu Regex vào Output
    llm_data.setdefault("invoice_info", {})
    for k, v in regex_data.get("invoice_info", {}).items():
        if v: llm_data["invoice_info"][k] = v
            
    llm_data.setdefault("seller_info", {})
    seller_tc = regex_data.get("seller_info", {}).get("tax_code")
    if seller_tc:
        llm_data["seller_info"]["tax_code"] = seller_tc
        company_info = get_company_by_tax_code(seller_tc)
        if company_info:
            llm_data["seller_info"]["legal_name"] = company_info.get("legal_name", "")
            llm_data["seller_info"]["address"] = company_info.get("address", "")
        
    llm_data.setdefault("buyer_info", {})
    buyer_tc = regex_data.get("buyer_info", {}).get("tax_code")
    if buyer_tc:
        llm_data["buyer_info"]["tax_code"] = buyer_tc
        company_info = get_company_by_tax_code(buyer_tc)
        if company_info:
            llm_data["buyer_info"]["legal_name"] = company_info.get("legal_name", "")
            llm_data["buyer_info"]["address"] = company_info.get("address", "")
        
    llm_data.setdefault("totals", {})
    if regex_data.get("totals", {}).get("total_amount_after_tax"):
        llm_data["totals"]["total_amount_after_tax"] = regex_data["totals"]["total_amount_after_tax"]
            
    return llm_data

def process_invoice(ocr_json_path):
    with open(ocr_json_path, "r", encoding="utf-8") as f:
        ocr_data = json.load(f)
        
    doc_id = ocr_data.get("document_id", ocr_json_path.stem)
    lines = ocr_data.get("lines", [])
    
    # 1. Regex Pre-processing (cần text phẳng)
    flat_text = "\n".join([line["text"] for line in lines])
    regex_result = extract_hard_fields(flat_text)
    
    # 2. BBox Clustering cho LLM (cần Markdown Table)
    md_table = cluster_and_format_markdown(lines)
    prompt = prompt_template.replace("{{OCR_TEXT}}", md_table)
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "keep_alive": 0
    }
    
    print(f"[{doc_id}] [START] Sending Markdown Table to Ollama...")
    
    # Retry loop
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(OLLAMA_API, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            response_text = result.get("response", "{}")
            try:
                parsed_json = json.loads(response_text)
            except json.JSONDecodeError:
                parsed_json = {}
                
            # 3. Merge Engine (MongoDB + Regex + LLM)
            merged_json = merge_results(parsed_json, regex_result)
            
            # 4. Validation Engine (Python calculation)
            final_json = run_validation_engine(merged_json)
            
            # 5. Lưu kết quả ra file JSON và đẩy lên MongoDB
            final_json["document_id"] = doc_id
            
            # Save output JSON
            out_file = OUTPUT_DIR / f"{doc_id}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(final_json, f, ensure_ascii=False, indent=2)
                
            # Push to MongoDB
            save_invoice(doc_id, final_json)
                
            status = final_json.get('workflow', {}).get('status')
            confidence = final_json.get('ai_metadata', {}).get('overall_confidence')
            icon = "[OK]" if status == "VALID" else "[WARN]"
            print(f"  {icon} Extracted {doc_id} -> Saved to DB (Status: {status}, Confidence: {confidence})")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"  [!] Attempt {attempt + 1}/{MAX_RETRIES} failed for {doc_id}: {e}")
            time.sleep(2)
            if attempt == MAX_RETRIES - 1:
                return False
        except Exception as e:
            print(f"  [ERROR] Error processing {doc_id}: {e}")
            return False
            
    return False

if __name__ == "__main__":
    try:
        requests.get("http://localhost:11434/")
    except Exception:
        print("Ollama is not running.")
        sys.exit(1)
        
    json_files = list(OCR_DIR.glob("*.json"))
    if not json_files:
        print("No OCR JSON files found!")
        sys.exit(0)
        
    print(f"Found {len(json_files)} invoices. Starting Database-Driven Pipeline V4...")
    
    success_count = 0
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_invoice, json_files))
        
    success_count = sum(1 for r in results if r)
    elapsed = time.time() - start_time
    print(f"ALL DONE. Processed {success_count}/{len(json_files)} invoices in {elapsed:.2f} seconds.")
