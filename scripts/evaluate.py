import os
import json
import csv
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = Path(r"d:\exe2\ai_invoice_dataset")
GROUND_TRUTH_DIR = BASE_DIR / "ground_truth"
PREDICTIONS_DIR = BASE_DIR / "llm_predictions" / "qwen25"
REPORTS_DIR = BASE_DIR / "reports"

FIELDS_TO_EVALUATE = [
    ("invoice_info", "invoice_no"),
    ("invoice_info", "issue_date"),
    ("seller_info", "tax_code"),
    ("seller_info", "legal_name"),
    ("buyer_info", "tax_code"),
    ("buyer_info", "legal_name"),
    ("totals", "total_amount_before_tax"),
    ("totals", "total_tax_amount"),
    ("totals", "total_amount_after_tax"),
]

def get_nested_value(data: Dict[str, Any], path: Tuple[str, str]) -> Any:
    """Safely get a nested value from a dictionary."""
    section, field = path
    if not isinstance(data, dict):
        return None
    return data.get(section, {}).get(field)

def normalize_value(val: Any) -> str:
    """Normalize values for string comparison."""
    if val is None or str(val).strip() == "":
        return ""
    if isinstance(val, (int, float)):
        # Format to 2 decimal places to handle floating point issues nicely
        return f"{float(val):.2f}"
    # Standardize strings: strip spaces, lower case
    return str(val).strip().lower()

class Evaluator:
    def __init__(self):
        self.results = []
        self.metrics = {
            "total_documents": 0,
            "perfect_documents": 0,
            "fields": {
                f"{section}.{field}": {"TP": 0, "FP": 0, "FN": 0, "TN": 0, "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1": 0.0}
                for section, field in FIELDS_TO_EVALUATE
            }
        }

    def evaluate_field(self, field_name: str, gt_val: Any, pred_val: Any) -> str:
        """Evaluate a single field and return the error type if any."""
        norm_gt = normalize_value(gt_val)
        norm_pred = normalize_value(pred_val)

        if norm_gt and norm_pred:
            if norm_gt == norm_pred:
                self.metrics["fields"][field_name]["TP"] += 1
                return "MATCH"
            else:
                self.metrics["fields"][field_name]["FP"] += 1
                if "tax_code" in field_name:
                    return "INVALID_TAX_CODE"
                return "VALUE_MISMATCH"
        elif norm_gt and not norm_pred:
            self.metrics["fields"][field_name]["FN"] += 1
            return "MISSING_FIELD"
        elif not norm_gt and norm_pred:
            self.metrics["fields"][field_name]["FP"] += 1
            return "EXTRA_FIELD_PREDICTED"
        else:
            self.metrics["fields"][field_name]["TN"] += 1
            return "MATCH" # Both missing as expected

    def evaluate_document(self, doc_id: str, gt_data: Dict[str, Any], pred_data: Dict[str, Any]):
        """Evaluate a single document."""
        self.metrics["total_documents"] += 1
        doc_result = {
            "document_id": doc_id,
            "fields": {},
            "document_perfect": True,
            "error_count": 0
        }

        for section, field in FIELDS_TO_EVALUATE:
            field_name = f"{section}.{field}"
            gt_val = get_nested_value(gt_data, (section, field))
            pred_val = get_nested_value(pred_data, (section, field))

            status = self.evaluate_field(field_name, gt_val, pred_val)
            
            doc_result["fields"][field_name] = {
                "ground_truth": gt_val,
                "prediction": pred_val,
                "status": status
            }

            if status != "MATCH":
                doc_result["document_perfect"] = False
                doc_result["error_count"] += 1

        if doc_result["document_perfect"]:
            self.metrics["perfect_documents"] += 1

        self.results.append(doc_result)

    def calculate_metrics(self):
        """Calculate final metrics like Accuracy, Precision, Recall, F1."""
        total_docs = self.metrics["total_documents"]
        if total_docs == 0:
            return

        for field_name, stats in self.metrics["fields"].items():
            tp = stats["TP"]
            fp = stats["FP"]
            fn = stats["FN"]
            tn = stats["TN"]
            
            total_cases = tp + fp + fn + tn
            accuracy = (tp + tn) / total_cases if total_cases > 0 else 0.0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

            stats["accuracy"] = accuracy * 100
            stats["precision"] = precision * 100
            stats["recall"] = recall * 100
            stats["f1"] = f1 * 100

        self.metrics["document_accuracy"] = (self.metrics["perfect_documents"] / total_docs) * 100

    def generate_reports(self):
        """Generate JSON and CSV reports."""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 1. JSON Report
        json_report_path = REPORTS_DIR / "evaluation_report.json"
        report_data = {
            "metrics": self.metrics,
            "document_details": self.results
        }
        with open(json_report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
            
        # 2. CSV Report
        csv_report_path = REPORTS_DIR / "evaluation_report.csv"
        csv_headers = ["document_id", "document_perfect", "error_count"]
        for section, field in FIELDS_TO_EVALUATE:
            field_name = f"{section}.{field}"
            csv_headers.extend([f"{field_name}_gt", f"{field_name}_pred", f"{field_name}_status"])
            
        with open(csv_report_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)
            
            for doc in self.results:
                row = [doc["document_id"], doc["document_perfect"], doc["error_count"]]
                for section, field in FIELDS_TO_EVALUATE:
                    field_name = f"{section}.{field}"
                    field_data = doc["fields"].get(field_name, {})
                    row.extend([
                        field_data.get("ground_truth", ""),
                        field_data.get("prediction", ""),
                        field_data.get("status", "UNKNOWN")
                    ])
                writer.writerow(row)
                
        logger.info(f"Reports saved to {REPORTS_DIR}")

    def print_console_report(self):
        """Print the formatted evaluation report to console."""
        print("\n" + "="*32)
        print("AI-INVOICE EVALUATION REPORT")
        print("============================")
        print(f"Documents: {self.metrics['total_documents']}\n")
        
        fields = self.metrics["fields"]
        
        # Calculate Combined Total Amount Accuracy
        total_acc = (
            fields['totals.total_amount_before_tax']['accuracy'] +
            fields['totals.total_tax_amount']['accuracy'] +
            fields['totals.total_amount_after_tax']['accuracy']
        ) / 3
        
        print(f"Invoice Number Accuracy: {fields['invoice_info.invoice_no']['accuracy']:.2f}%")
        print(f"Issue Date Accuracy: {fields['invoice_info.issue_date']['accuracy']:.2f}%")
        print(f"Seller Tax Code Accuracy: {fields['seller_info.tax_code']['accuracy']:.2f}%")
        print(f"Buyer Tax Code Accuracy: {fields['buyer_info.tax_code']['accuracy']:.2f}%")
        print(f"Total Amount Accuracy: {total_acc:.2f}%")
        
        # Overall Accuracy
        all_field_accuracies = [stats['accuracy'] for stats in fields.values()]
        overall_acc = sum(all_field_accuracies) / len(all_field_accuracies) if all_field_accuracies else 0.0
        
        print(f"\nOverall Accuracy: {overall_acc:.2f}%")
        print(f"Document Accuracy (Perfect Docs): {self.metrics['document_accuracy']:.2f}%")
        print("================================\n")

def main():
    logger.info("Starting AI-Invoice Evaluation Framework...")
    
    if not GROUND_TRUTH_DIR.exists():
        logger.error(f"Ground truth directory not found: {GROUND_TRUTH_DIR}")
        logger.info("Please create ground truth files before evaluating.")
        return

    if not PREDICTIONS_DIR.exists():
        logger.error(f"Predictions directory not found: {PREDICTIONS_DIR}")
        return

    gt_files = {f.stem: f for f in GROUND_TRUTH_DIR.glob("*.json")}
    pred_files = {f.stem: f for f in PREDICTIONS_DIR.glob("*.json")}
    
    if not gt_files:
        logger.warning(f"No ground truth JSON files found in {GROUND_TRUTH_DIR}")
        return

    evaluator = Evaluator()

    for doc_id, gt_path in gt_files.items():
        if doc_id not in pred_files:
            logger.warning(f"Prediction missing for document: {doc_id}")
            continue
            
        with open(gt_path, "r", encoding="utf-8") as f:
            gt_data = json.load(f)
            
        pred_path = pred_files[doc_id]
        with open(pred_path, "r", encoding="utf-8") as f:
            pred_data = json.load(f)
            
        evaluator.evaluate_document(doc_id, gt_data, pred_data)

    evaluator.calculate_metrics()
    evaluator.generate_reports()
    evaluator.print_console_report()

if __name__ == "__main__":
    main()
