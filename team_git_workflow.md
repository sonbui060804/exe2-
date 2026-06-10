# CHIẾN LƯỢC LÀM VIỆC NHÓM TRÊN GIT (Dành cho Team 5 người)

Để đảm bảo 4 người bạn của bạn cùng vào code mà **nhánh chính (main) không bao giờ bị lỗi**, code luôn sạch (clean) và không bị "chửi nhau" vì đè code của nhau, toàn team BẮT BUỘC phải tuân thủ quy trình **GitHub Flow** dưới đây:

## ❌ QUY TẮC SỐ 1 (Tử Huyệt): TUYỆT ĐỐI KHÔNG PUSH THẲNG VÀO `main`
Nhánh `main` là bộ mặt của dự án, là bản code luôn luôn phải chạy được (để còn đem đi demo khách hàng). Bất cứ ai code tính năng mới cũng **không được phép** `git push origin main`.

---

## ✅ QUY TRÌNH CHUẨN KHI CODE (4 BƯỚC)

### BƯỚC 1: Cập nhật code mới nhất & Tạo nhánh riêng (Branching)
Mỗi khi bắt đầu làm 1 task mới, hãy lấy code mới nhất từ mạng về và tạo 1 nhánh (branch) riêng cho mình.
```bash
# Lấy code mới nhất từ nhánh main
git checkout main
git pull origin main

# Tạo nhánh mới có tên theo task (VD: Vinh làm tính năng Export)
git checkout -b feat/vinh-export-misa
```
*Quy tắc đặt tên nhánh:*
- Tính năng mới: `feat/tên-bạn-tên-tính-năng` (VD: `feat/hung-login`)
- Sửa lỗi: `fix/tên-bạn-tên-lỗi` (VD: `fix/anh-loi-mau-nut-bam`)

### BƯỚC 2: Code và Commit trên nhánh của mình
Cứ code bình thường. Cuối ngày hoặc xong 1 phần thì commit lại.
```bash
git add .
git commit -m "feat: Đã làm xong nút Export Misa"
```
*Quy tắc viết Commit:* Rõ ràng, tiếng Việt hoặc tiếng Anh nhưng phải biết mình vừa làm gì.

### BƯỚC 3: Đồng bộ lại với nhóm trước khi đẩy lên (Cực kỳ quan trọng)
Trong lúc bạn code, có thể người khác đã đẩy code mới lên `main` rồi. Nếu bạn đẩy luôn sẽ bị "Xung đột" (Conflict).
```bash
# Vẫn đang ở nhánh của mình, tải code main mới nhất về gộp vào
git pull origin main
```
*(Nếu có Conflict, code bị bôi đỏ, 2 người gọi điện cho nhau để thống nhất giữ lại dòng code nào. Xong xuôi thì chạy tiếp máy ảo để test. Test chạy mượt không lỗi lầm gì mới qua Bước 4).*

### BƯỚC 4: Đẩy nhánh lên GitHub và Tạo Pull Request (PR)
Đẩy nhánh của bạn lên mạng:
```bash
git push origin feat/vinh-export-misa
```
- Lên trang web GitHub, bạn sẽ thấy nút xanh **"Compare & pull request"**. Bấm vào đó.
- Nhờ 1 người khác (hoặc bạn là Leader) vào xem lại (Review Code). 
- Nếu code chuẩn, không lỗi, Leader sẽ bấm **"Merge pull request"**. Lúc này code mới chính thức được gộp vào nhánh `main`.

---

## 💡 TÓM LẠI CHO DỄ NHỚ:
1. Sáng mở máy: `git checkout main` -> `git pull` -> `git checkout -b nhanh-cua-toi`.
2. Trưa/Chiều code: `git add .` -> `git commit -m "làm abc"`.
3. Tối đẩy code: `git pull origin main` (xử lý lỗi nếu có) -> `git push origin nhanh-cua-toi`.
4. Lên web tạo **Pull Request** nhờ anh em duyệt.

👉 Hãy gửi file này cho 4 người bạn kia đọc để cả team có một văn hóa code chuyên nghiệp như các tập đoàn công nghệ lớn!
