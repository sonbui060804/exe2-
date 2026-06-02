import json
import requests
from pathlib import Path
import sys
import time

BASE_DIR = Path(r"d:\exe2\ai_invoice_dataset")
OCR_DIR = BASE_DIR / "ocr" / "paddleocr"
GT_DIR = BASE_DIR / "ground_truth"
PROMPT_FILE = BASE_DIR / "schemas" / "gt_generation_prompt.txt"
SCHEMA_FILE = BASE_DIR / "schemas" / "invoice_schema_v1.json"

GT_DIR.mkdir(parents=True, exist_ok=True)

with open(PROMPT_FILE, "r", encoding="utf-8") as f:
    prompt_template = f.read()

with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    schema_content = f.read()
    
if "{{SCHEMA}}" not in prompt_template:
    prompt_template += "\n\nINVOICE_SCHEMA:\n{{SCHEMA}}"

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

def generate_gt(ocr_json_path):
    with open(ocr_json_path, "r", encoding="utf-8") as f:
        ocr_data = json.load(f)
        
    doc_id = ocr_data.get("document_id", ocr_json_path.stem)
    
    out_file = GT_DIR / f"{doc_id}.json"
    if out_file.exists():
        return True
        
    lines = ocr_data.get("lines", [])
    extracted_text = "\n".join([line["text"] for line in lines])
    
    prompt = prompt_template.replace("{{OCR_TEXT}}", extracted_text)
    prompt = prompt.replace("{{SCHEMA}}", schema_content)
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "keep_alive": 0
    }
    
    print(f"[{doc_id}] [START] Generating Ground Truth...")
    
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(OLLAMA_API, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            
            response_text = result.get("response", "{}")
            parsed_json = json.loads(response_text)
            
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(parsed_json, f, ensure_ascii=False, indent=2)
                
            print(f"  [OK] Saved semi-auto GT: {out_file.name}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"  [!] Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
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
        
    ocr_files = list(OCR_DIR.glob("*.json"))
    print(f"Found {len(ocr_files)} OCR files.")
    
    generated = 0
    for file in ocr_files:
        if not (GT_DIR / f"{file.stem}.json").exists():
            if generate_gt(file):
                generated += 1
            
    print(f"Done. Processed {generated} new files.")
