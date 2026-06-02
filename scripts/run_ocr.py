from paddleocr import PaddleOCR
import json
from pathlib import Path
from datetime import datetime

# Note: Changed lang="en" to "vi" to correctly recognize Vietnamese VAT invoices
ocr = PaddleOCR(
    use_angle_cls=True,
    lang="vi"
)

INPUT_DIR = Path(r"d:\exe2\ai_invoice_dataset\invoices\raw")
OUTPUT_DIR = Path(r"d:\exe2\ai_invoice_dataset\ocr\paddleocr")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}

for image_file in INPUT_DIR.iterdir():
    if image_file.suffix.lower() not in SUPPORTED_EXTENSIONS:
        continue

    print(f"Processing {image_file.name}")
    result = ocr.ocr(str(image_file))
    lines = []
    
    if result and result[0]:
        for page in result:
            if page:
                for item in page:
                    bbox = item[0]
                    text = item[1][0]
                    confidence = float(item[1][1])

                    lines.append({
                        "text": text,
                        "confidence": confidence,
                        "bbox": bbox
                    })

    output = {
        "document_id": image_file.stem,
        "source_file": image_file.name,
        "ocr_engine": "PaddleOCR",
        "processed_at": datetime.utcnow().isoformat(),
        "lines": lines
    }

    output_file = OUTPUT_DIR / f"{image_file.stem}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2
        )

print("DONE")
