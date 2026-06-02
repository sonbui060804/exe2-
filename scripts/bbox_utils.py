def cluster_and_format_markdown(lines):
    """
    Nhóm các dòng OCR lại theo tọa độ Y (cùng 1 dòng trên hóa đơn)
    Và sắp xếp theo tọa độ X. Xuất ra Markdown Table.
    """
    if not lines:
        return ""
        
    # Tính tâm Y cho mỗi line
    for line in lines:
        bbox = line["bbox"]
        # bbox là [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        # Y center = (y1 + y3) / 2
        y_center = (bbox[0][1] + bbox[2][1]) / 2
        line["y_center"] = y_center
        line["x_center"] = (bbox[0][0] + bbox[2][0]) / 2

    # Sắp xếp theo Y từ trên xuống dưới
    lines.sort(key=lambda x: x["y_center"])
    
    rows = []
    current_row = [lines[0]]
    
    # Nhóm thành các dòng nếu chênh lệch Y nhỏ hơn 15 pixel (tùy độ phân giải, thường hóa đơn là 10-20px)
    for line in lines[1:]:
        if abs(line["y_center"] - current_row[0]["y_center"]) < 15:
            current_row.append(line)
        else:
            # Sắp xếp các ô trong dòng theo X từ trái qua phải
            current_row.sort(key=lambda x: x["x_center"])
            rows.append(current_row)
            current_row = [line]
            
    if current_row:
        current_row.sort(key=lambda x: x["x_center"])
        rows.append(current_row)
        
    # Tạo Markdown text
    md_lines = []
    for row in rows:
        texts = [item["text"] for item in row]
        # Gom các item thành một dòng, phân cách bằng |
        md_lines.append("| " + " | ".join(texts) + " |")
        
    return "\n".join(md_lines)
