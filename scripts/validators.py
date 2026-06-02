import re

def run_validation_engine(final_json):
    """
    Validation Engine V2 (Pure Python Rules)
    - Không ép LLM tính toán.
    - Python tính lại subtotal và tax từ items.
    """
    errors = []
    
    items = final_json.get("items", [])
    if not isinstance(items, list): items = []
    
    # 1. Tính toán lại subtotal và tax từ line items
    calculated_subtotal = 0
    calculated_tax = 0
    for item in items:
        if not isinstance(item, dict): continue
        amt = item.get("amount_before_tax") or 0
        qty = item.get("quantity") or 1
        price = item.get("unit_price") or 0
        
        # Nếu amount_before_tax trống nhưng có qty và price, tự tính
        if not amt and qty and price:
            try:
                amt = float(qty) * float(price)
                item["amount_before_tax"] = amt
            except:
                pass
                
        try:
            calculated_subtotal += float(amt)
        except:
            pass
            
        tax_amt = item.get("tax_amount") or 0
        if not tax_amt and amt:
            tax_rate = item.get("tax_rate")
            if tax_rate is not None and str(tax_rate) != "":
                try:
                    tax_amt = float(amt) * float(tax_rate) / 100
                    item["tax_amount"] = tax_amt
                except:
                    pass
        try:
            calculated_tax += float(tax_amt)
        except:
            pass
            
    totals = final_json.get("totals", {})
    if not isinstance(totals, dict): totals = {}
    
    # Regex (totals.total_amount_after_tax) là số tiền chắc chắn nhất vì nó nằm to đùng cuối hóa đơn
    grand_total_regex = totals.get("total_amount_after_tax", 0)
    
    if grand_total_regex:
        try:
            grand_total_regex = float(grand_total_regex)
        except:
            grand_total_regex = 0
            
        # Nếu tổng tiền sau thuế của Regex không khớp với subtotal + tax
        if abs(grand_total_regex - (calculated_subtotal + calculated_tax)) > 1000:
            # Nếu chênh lệch quá lớn, ta có thể tin tưởng Grand Total từ Regex hơn, và ghi đè lại subtotal/tax
            # (Giả định thuế 10%)
            if calculated_subtotal == 0 or abs(calculated_subtotal + calculated_tax) < 1:
                calculated_subtotal = grand_total_regex / 1.1
                calculated_tax = grand_total_regex - calculated_subtotal
                
    totals["total_amount_before_tax"] = round(calculated_subtotal, 2)
    totals["total_tax_amount"] = round(calculated_tax, 2)
    totals["total_amount_after_tax"] = round(grand_total_regex if grand_total_regex else (calculated_subtotal + calculated_tax), 2)
    
    final_json["totals"] = totals
    
    # Validation Rules
    if not final_json.get("seller_info", {}).get("tax_code"):
        errors.append("MISSING_SELLER_TAX_CODE")
    if not final_json.get("buyer_info", {}).get("tax_code"):
        errors.append("MISSING_BUYER_TAX_CODE")
    if not final_json.get("invoice_info", {}).get("invoice_no"):
        errors.append("MISSING_INVOICE_NO")
        
    final_json["validation_errors"] = errors
    
    # Confidence Scoring
    base_confidence = 1.0
    if "MISSING_SELLER_TAX_CODE" in errors: base_confidence -= 0.3
    if "MISSING_BUYER_TAX_CODE" in errors: base_confidence -= 0.3
    if "MISSING_INVOICE_NO" in errors: base_confidence -= 0.2
    
    final_json["ai_metadata"] = {"overall_confidence": max(0.1, round(base_confidence, 2))}
    final_json["workflow"] = {"status": "VALID" if base_confidence >= 0.8 else "PENDING_REVIEW"}
    
    return final_json
