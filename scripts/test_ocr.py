import json
import glob

# Try to find the first JSON file automatically
json_files = glob.glob(r"d:\exe2\ai_invoice_dataset\ocr\paddleocr\*.json")
if json_files:
    test_file = json_files[0]
    print(f"Testing OCR file: {test_file}\n" + "-"*40)
    with open(test_file, encoding="utf-8") as f:
        data = json.load(f)

    for line in data.get("lines", []):
        print(line["text"])
else:
    print("No JSON files found in ocr/paddleocr!")
