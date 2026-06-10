import os
import random
from PIL import Image, ImageDraw, ImageFont
import json

output_dir = r"d:\exe2\ai_invoice_dataset\invoices\raw"
gt_dir = r"d:\exe2\ai_invoice_dataset\ground_truth"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(gt_dir, exist_ok=True)
random.seed(42)

try:
    font_title = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 30)
    font_text = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 18)
    font_bold = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 18)
    font_misa_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 26)
except IOError:
    print("Warning: Không tìm thấy font Arial, tiếng Việt có thể bị lỗi.")
    font_title = ImageFont.load_default()
    font_text = ImageFont.load_default()
    font_bold = ImageFont.load_default()
    font_misa_title = ImageFont.load_default()

def draw_default(d, data, offset_x, offset_y, color_main):
    # Header
    d.text((280 + offset_x, 50 + offset_y), "HÓA ĐƠN GIÁ TRỊ GIA TĂNG", fill=color_main, font=font_title)
    d.text((340 + offset_x, 90 + offset_y), "(Bản thể hiện của hóa đơn điện tử)", fill=(0, 0, 0), font=font_text)
    
    d.text((650, 130), f"Ký hiệu mẫu số: 1C26TAA", fill=(0, 0, 0), font=font_text)
    d.text((650, 160), f"Ký hiệu hóa đơn: AA/26E", fill=(0, 0, 0), font=font_text)
    d.text((650, 190), f"Số: {data['invoice_no']}", fill=(255, 0, 0), font=font_bold)
    d.text((650, 220), f"Ngày: 02/06/2026", fill=(0, 0, 0), font=font_text)
    
    # Seller
    d.text((50, 130), "Đơn vị bán: CÔNG TY CỔ PHẦN CÔNG NGHỆ AI-INVOICE", fill=color_main, font=font_bold)
    d.text((50, 160), "Mã số thuế: 0101234567", fill=(0, 0, 0), font=font_text)
    d.text((50, 190), "Địa chỉ: Số 1 Đường AI, Phường Công Nghệ, Quận Mới, Hà Nội", fill=(0, 0, 0), font=font_text)
    
    d.line([(50, 260), (850, 260)], fill=color_main, width=2)
    
    # Buyer
    d.text((50, 280), f"Đơn vị mua: {data['buyer_name']}", fill=(0, 0, 0), font=font_bold)
    d.text((50, 310), f"Mã số thuế: {data['buyer_tax_code']}", fill=(0, 0, 0), font=font_text)
    d.text((50, 340), "Địa chỉ: Khu công nghiệp ABC, TP. Hồ Chí Minh", fill=(0, 0, 0), font=font_text)
    d.text((50, 370), "Hình thức thanh toán: TM/CK", fill=(0, 0, 0), font=font_text)
    
    d.line([(50, 410), (850, 410)], fill=color_main, width=2)
    
    # Items
    d.text((50, 430), "STT", fill=(0, 0, 0), font=font_bold)
    d.text((120, 430), "Tên hàng hóa, dịch vụ", fill=(0, 0, 0), font=font_bold)
    d.text((450, 430), "ĐVT", fill=(0, 0, 0), font=font_bold)
    d.text((520, 430), "Số lượng", fill=(0, 0, 0), font=font_bold)
    d.text((630, 430), "Đơn giá", fill=(0, 0, 0), font=font_bold)
    d.text((750, 430), "Thành tiền", fill=(0, 0, 0), font=font_bold)
    d.line([(50, 460), (850, 460)], fill=(0, 0, 0), width=1)
    
    d.text((50, 480), "1", fill=(0, 0, 0), font=font_text)
    d.text((120, 480), "Bản quyền phần mềm OCR", fill=(0, 0, 0), font=font_text)
    d.text((450, 480), "Năm", fill=(0, 0, 0), font=font_text)
    d.text((520, 480), "1", fill=(0, 0, 0), font=font_text)
    d.text((630, 480), f"{data['price1']:,}", fill=(0, 0, 0), font=font_text)
    d.text((750, 480), f"{data['price1']:,}", fill=(0, 0, 0), font=font_text)
    
    d.text((50, 520), "2", fill=(0, 0, 0), font=font_text)
    d.text((120, 520), "Dịch vụ bảo trì hệ thống", fill=(0, 0, 0), font=font_text)
    d.text((450, 520), "Giờ", fill=(0, 0, 0), font=font_text)
    d.text((520, 520), "10", fill=(0, 0, 0), font=font_text)
    d.text((630, 520), f"{int(data['price2']/10):,}", fill=(0, 0, 0), font=font_text)
    d.text((750, 520), f"{data['price2']:,}", fill=(0, 0, 0), font=font_text)
    d.line([(50, 560), (850, 560)], fill=color_main, width=2)
    
    d.text((450, 580), "Cộng tiền hàng:", fill=(0, 0, 0), font=font_bold)
    d.text((750, 580), f"{data['total_goods']:,}", fill=(0, 0, 0), font=font_bold)
    d.text((450, 620), "Thuế suất GTGT: 10%", fill=(0, 0, 0), font=font_bold)
    d.text((650, 620), "Tiền thuế:", fill=(0, 0, 0), font=font_bold)
    d.text((750, 620), f"{data['tax']:,}", fill=(0, 0, 0), font=font_bold)
    d.text((450, 660), "Tổng tiền thanh toán:", fill=(0, 0, 0), font=font_bold)
    d.text((750, 660), f"{data['total']:,}", fill=(0, 0, 0), font=font_bold)

def draw_misa(d, data, offset_x, offset_y, color_main):
    d.rectangle([(0,0), (900, 120)], fill=color_main)
    d.text((280 + offset_x, 20 + offset_y), "HÓA ĐƠN GIÁ TRỊ GIA TĂNG", fill=(255, 255, 255), font=font_misa_title)
    d.text((380 + offset_x, 60 + offset_y), "(MISA Template)", fill=(200, 200, 200), font=font_text)
    
    d.text((50, 140), "CÔNG TY CỔ PHẦN CÔNG NGHỆ AI-INVOICE", fill=(0, 0, 0), font=font_bold)
    d.text((50, 170), "Mã số thuế: 0101234567", fill=(0, 0, 0), font=font_bold)
    
    d.text((600, 140), f"Ký hiệu: 1C26TAA", fill=(0, 0, 0), font=font_text)
    d.text((600, 170), f"Số Hóa Đơn: {data['invoice_no']}", fill=(255, 0, 0), font=font_bold)
    d.text((600, 200), f"Ngày xuất: 02/06/2026", fill=(0, 0, 0), font=font_text)
    
    d.line([(50, 240), (850, 240)], fill=color_main, width=2)
    
    d.text((50, 260), f"Khách hàng: {data['buyer_name']}", fill=(0, 0, 0), font=font_bold)
    d.text((50, 290), f"MST Khách hàng: {data['buyer_tax_code']}", fill=(0, 0, 0), font=font_text)
    
    d.rectangle([(50, 350), (850, 390)], fill=(200, 220, 255))
    d.text((60, 360), "STT", fill=(0, 0, 0), font=font_bold)
    d.text((120, 360), "Tên Hàng Hóa", fill=(0, 0, 0), font=font_bold)
    d.text((500, 360), "SL", fill=(0, 0, 0), font=font_bold)
    d.text((600, 360), "Đơn giá", fill=(0, 0, 0), font=font_bold)
    d.text((750, 360), "Thành tiền", fill=(0, 0, 0), font=font_bold)
    
    d.text((60, 410), "1", fill=(0, 0, 0), font=font_text)
    d.text((120, 410), "Bản quyền phần mềm OCR", fill=(0, 0, 0), font=font_text)
    d.text((500, 410), "1", fill=(0, 0, 0), font=font_text)
    d.text((600, 410), f"{data['price1']:,}", fill=(0, 0, 0), font=font_text)
    d.text((750, 410), f"{data['price1']:,}", fill=(0, 0, 0), font=font_text)
    
    d.text((60, 450), "2", fill=(0, 0, 0), font=font_text)
    d.text((120, 450), "Dịch vụ bảo trì hệ thống", fill=(0, 0, 0), font=font_text)
    d.text((500, 450), "10", fill=(0, 0, 0), font=font_text)
    d.text((600, 450), f"{int(data['price2']/10):,}", fill=(0, 0, 0), font=font_text)
    d.text((750, 450), f"{data['price2']:,}", fill=(0, 0, 0), font=font_text)
    
    d.line([(50, 500), (850, 500)], fill=color_main, width=1)
    
    d.text((500, 520), "Tổng tiền chưa thuế:", fill=(0, 0, 0), font=font_text)
    d.text((750, 520), f"{data['total_goods']:,}", fill=(0, 0, 0), font=font_bold)
    d.text((500, 550), "Thuế GTGT (10%):", fill=(0, 0, 0), font=font_text)
    d.text((750, 550), f"{data['tax']:,}", fill=(0, 0, 0), font=font_bold)
    d.text((500, 580), "TỔNG THANH TOÁN:", fill=(0, 0, 0), font=font_bold)
    d.text((750, 580), f"{data['total']:,}", fill=(255, 0, 0), font=font_bold)

def draw_fast(d, data, offset_x, offset_y, color_main):
    d.text((50 + offset_x, 50 + offset_y), "HÓA ĐƠN ĐIỆN TỬ (FAST)", fill=color_main, font=font_title)
    
    d.text((50, 100), "Đơn vị bán:", fill=(0, 0, 0), font=font_text)
    d.text((150, 100), "CÔNG TY CỔ PHẦN CÔNG NGHỆ AI-INVOICE", fill=(0, 0, 0), font=font_bold)
    d.text((50, 130), "MST:", fill=(0, 0, 0), font=font_text)
    d.text((150, 130), "0101234567", fill=(0, 0, 0), font=font_bold)
    
    d.text((600, 50), f"Ký hiệu: 1C26TAA", fill=(0, 0, 0), font=font_text)
    d.text((600, 80), f"Số: {data['invoice_no']}", fill=(0, 0, 0), font=font_bold)
    d.text((600, 110), f"Ngày: 02/06/2026", fill=(0, 0, 0), font=font_text)
    
    d.line([(50, 170), (850, 170)], fill=(0, 0, 0), width=1)
    
    d.text((50, 190), f"Tên khách hàng: {data['buyer_name']}", fill=(0, 0, 0), font=font_bold)
    d.text((50, 220), f"Mã số thuế: {data['buyer_tax_code']}", fill=(0, 0, 0), font=font_text)
    
    d.line([(50, 270), (850, 270)], fill=(0, 0, 0), width=1)
    d.text((50, 280), "STT | Tên hàng hóa dịch vụ | ĐVT | SL | Đơn giá | Thành tiền", fill=(0, 0, 0), font=font_bold)
    d.line([(50, 310), (850, 310)], fill=(0, 0, 0), width=1)
    
    d.text((50, 330), f"1 | Bản quyền phần mềm OCR | Năm | 1 | {data['price1']:,} | {data['price1']:,}", fill=(0, 0, 0), font=font_text)
    d.text((50, 370), f"2 | Dịch vụ bảo trì hệ thống | Giờ | 10 | {int(data['price2']/10):,} | {data['price2']:,}", fill=(0, 0, 0), font=font_text)
    
    d.line([(50, 410), (850, 410)], fill=(0, 0, 0), width=1)
    
    d.text((500, 430), f"Cộng tiền hàng: {data['total_goods']:,}", fill=(0, 0, 0), font=font_text)
    d.text((500, 460), f"Tiền thuế GTGT: {data['tax']:,}", fill=(0, 0, 0), font=font_text)
    d.text((500, 490), f"Tổng cộng tiền thanh toán: {data['total']:,}", fill=color_main, font=font_bold)


buyer_names = ["CÔNG TY TNHH THƯƠNG MẠI ALPHA", "CÔNG TY CỔ PHẦN BETA", "DOANH NGHIỆP TƯ NHÂN GAMMA", "TẬP ĐOÀN ĐỈNH CAO", "CÔNG TY XUẤT NHẬP KHẨU Z"]
colors = [(0,0,0), (0, 50, 150), (150, 0, 0), (0, 150, 50), (100, 0, 100), (255, 100, 0)]
bg_colors = [(255, 255, 255), (250, 250, 240), (240, 250, 255), (255, 240, 240)]

for i in range(1, 101):
    bg_color = random.choice(bg_colors)
    img = Image.new('RGB', (900, 800), color=bg_color)
    d = ImageDraw.Draw(img)
    
    invoice_no = f"{i:07d}"
    doc_id = f"INV_20260602_{invoice_no}"
    
    buyer = random.choice(buyer_names)
    buyer_tax_code = f"030{random.randint(1000000, 9999999)}"
    
    price1 = random.randint(10, 50) * 100000
    price2 = random.randint(5, 20) * 100000
    total_goods = price1 + price2
    tax = int(total_goods * 0.1)
    total = total_goods + tax
    
    data = {
        'invoice_no': invoice_no,
        'buyer_name': buyer,
        'buyer_tax_code': buyer_tax_code,
        'price1': price1,
        'price2': price2,
        'total_goods': total_goods,
        'tax': tax,
        'total': total
    }
    
    template_type = random.choice(["DEFAULT", "MISA", "FAST"])
    
    offset_x = random.randint(-20, 20)
    offset_y = random.randint(-10, 10)
    color_main = random.choice(colors)
    
    if template_type == "MISA":
        draw_misa(d, data, offset_x, offset_y, color_main)
    elif template_type == "FAST":
        draw_fast(d, data, offset_x, offset_y, color_main)
    else:
        draw_default(d, data, offset_x, offset_y, color_main)
        
    file_path = os.path.join(output_dir, f"{doc_id}.png")
    img.save(file_path)
    
    gt_data = {
      "template_type": template_type,
      "invoice_info": {
        "invoice_no": invoice_no,
        "issue_date": "2026-06-02"
      },
      "seller_info": {
        "tax_code": "0101234567",
        "legal_name": "CÔNG TY CỔ PHẦN CÔNG NGHỆ AI-INVOICE"
      },
      "buyer_info": {
        "tax_code": buyer_tax_code,
        "legal_name": buyer
      },
      "totals": {
        "total_amount_before_tax": total_goods,
        "total_tax_amount": tax,
        "total_amount_after_tax": total
      }
    }
    with open(os.path.join(gt_dir, f"{doc_id}.json"), "w", encoding="utf-8") as f:
        json.dump(gt_data, f, ensure_ascii=False, indent=2)

print(f"Successfully generated 100 mock invoices with randomized styles (MISA, FAST, DEFAULT) and 100 Perfect Ground Truths.")
