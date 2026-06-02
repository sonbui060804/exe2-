import re

def extract_hard_fields(text):
    """
    Trích xuất các trường cố định bằng Regex, bao gồm tính năng chịu lỗi OCR (OCR-tolerant).
    """
    result = {
        "invoice_info": {},
        "seller_info": {},
        "buyer_info": {},
        "totals": {}
    }
    
    # 1. Số hóa đơn (Invoice Number)
    # OCR lỗi phổ biến: Số, Só, So, S6, Sô
    inv_no_match = re.search(r"(?:Số|Só|So|S6|Sô|S6:)\s*:?\s*(\d{6,8})", text, re.IGNORECASE)
    if inv_no_match:
        result["invoice_info"]["invoice_no"] = inv_no_match.group(1)
        
    # 2. Mã số thuế (Tax Code)
    # Tìm tất cả MST trong văn bản. Thường MST đầu tiên là của người bán, cái thứ 2 là của người mua.
    # Lỗi OCR: 0 có thể bị đọc thành O (chữ O).
    mst_matches = re.findall(r"(?:MST|Mã số thuế|Ma s[oó] thu[eéế]|Ma so thue|MS\s*T)\s*:?\s*([0-9O\-\.\ ]{10,15})", text, re.IGNORECASE)
    
    clean_msts = []
    for m in mst_matches:
        # Làm sạch: xóa khoảng trắng, gạch nối, dấu chấm, đổi chữ O thành số 0
        cleaned = re.sub(r"[\s\-\.]", "", m).replace("O", "0").replace("o", "0")
        if len(cleaned) in [10, 13, 14]:
            clean_msts.append(cleaned)
            
    if len(clean_msts) >= 1:
        result["seller_info"]["tax_code"] = clean_msts[0]
    if len(clean_msts) >= 2:
        result["buyer_info"]["tax_code"] = clean_msts[1]
        
    # 3. Ngày phát hành (Issue Date)
    date_match = re.search(r"(\d{2})[\/\-\.](\d{2})[\/\-\.](\d{4})", text)
    if date_match:
        result["invoice_info"]["issue_date"] = f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}"
        
    # 4. Ký hiệu mẫu số (Form Number)
    form_no_match = re.search(r"(?:mẫu số|mau so|mãu số|màu số)[^\d]*([0-9][A-Z0-9]{5,6})", text, re.IGNORECASE)
    if form_no_match:
        result["invoice_info"]["form_no"] = form_no_match.group(1).upper()
        
    # 5. Ký hiệu hóa đơn (Serial Number)
    serial_no_match = re.search(r"(?:ký hiệu|ky hieu|kỳ hiệu)[^\w]*([A-Z0-9]{2}/[0-9]{2}[A-Z])", text, re.IGNORECASE)
    if serial_no_match:
        result["invoice_info"]["serial_no"] = serial_no_match.group(1).upper()
        
    # 6. Hình thức thanh toán (Payment Method)
    payment_match = re.search(r"(?:Thanh toán|thanh toan|Hinh thuc|Hinh thurc).*?(TM/CK|TM|CK)", text, re.IGNORECASE)
    if payment_match:
        result["invoice_info"]["payment_method"] = payment_match.group(1).upper()

    # Bắt tổng tiền chuẩn bằng Regex ngược (tìm từ dưới lên)
    # Xử lý các trường hợp lỗi OCR mất dấu như: "Tng tin thanh ton", "cng tin hang"
    grand_match = re.search(r"(?:Tổng tiền thanh toán|Tong tien thanh toan|T[oô]ng ti[eê]n|Tng tin thanh ton).*?([\d\.\,]{6,})", text, re.IGNORECASE)
    if grand_match:
        val = float(re.sub(r"[^\d]", "", grand_match.group(1)))
        result["totals"]["total_amount_after_tax"] = val
    else:
        # Thử tìm con số lớn nhất nằm ở nửa dưới văn bản
        numbers = re.findall(r"[\d\.\,]{6,}", text[len(text)//2:])
        if numbers:
            biggest = max([float(re.sub(r"[^\d]", "", n)) for n in numbers])
            result["totals"]["total_amount_after_tax"] = biggest
        
    # 7. Tiền tệ (Currency)
    if re.search(r"\bUSD\b", text):
        result["invoice_info"]["currency"] = "USD"
    elif re.search(r"\bEUR\b", text):
        result["invoice_info"]["currency"] = "EUR"
    else:
        result["invoice_info"]["currency"] = "VND"
        
    return result
