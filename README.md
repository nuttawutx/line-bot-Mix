# 📋 LINE Bot สำหรับลงทะเบียนพนักงานอัตโนมัติ

ระบบ LINE Bot ที่เชื่อมต่อกับ Google Sheets ช่วยให้พนักงานลงทะเบียนผ่าน LINE ได้ทันที พร้อมสร้างรหัสพนักงานอัตโนมัติ และแยกประเภทพนักงาน (รายวัน/รายเดือน)

## 🚀 ฟีเจอร์เด่น
- ลงทะเบียนผ่าน LINE เพียงส่งข้อความ 6 บรรทัด
- แยกข้อมูลลง Google Sheet ตามประเภท
- สร้างรหัสพนักงานใหม่อัตโนมัติ
- รองรับการเปิด/ปิดระบบจาก Google Sheets และสั่งจาก LINE
- มีระบบ Admin เฉพาะผู้ดูแล

## 🔧 เครื่องมือที่ใช้
- Python 3.x + Flask
- gspread + Google API
- LINE Messaging API
- Render (สำหรับ deploy ระบบ)

## ⚙️ วิธีติดตั้ง (Local)
1. สร้าง Google Service Account และโหลด JSON
2. แปลงเป็น base64 แล้วสร้าง `.env`:
GOOGLE_CREDENTIAL_BASE64=...
LINE_CHANNEL_ACCESS_TOKEN_1=...
LINE_CHANNEL_SECRET_1=...
3. ติดตั้ง dependencies:
pip install -r requirements.txt
4. รันเซิร์ฟเวอร์:
python app.py


## 💬 ตัวอย่างข้อความที่ต้องส่งใน LINE
ชื่อ: สมชาย ใจดี
ชื่อเล่น: ชาย
สาขา: บางนา
ตำแหน่ง: พนักงานขาย
เริ่มงาน: 10-07-2025
ประเภท: รายวัน


## 📌 ผู้พัฒนา
[Your Name: Nut]  
Email: nuttawutchars@gmail.com 
GitHub: github.com/nuttawutx 

