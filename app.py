# === Shared Setup ===
import os
import json
import base64
import re
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
from datetime import datetime
import pytz
import requests

load_dotenv()

GOOGLE_CREDENTIAL_BASE64 = os.getenv("GOOGLE_CREDENTIAL_BASE64")
SYSTEM_ACTIVE = os.getenv("SYSTEM_ACTIVE", "true").lower() == "true"

cred_path = "google-credentials.json"
if GOOGLE_CREDENTIAL_BASE64:
    with open(cred_path, "w") as f:
        f.write(base64.b64decode(GOOGLE_CREDENTIAL_BASE64).decode("utf-8"))

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(cred_path, scope)
client = gspread.authorize(creds)

app = Flask(__name__)

def register_employee(event, line_bot_api, worksheet_name, spreadsheet_name, webhook_env_var, default_code, prefix=""):
    if not SYSTEM_ACTIVE:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="⚠️ ขณะนี้ระบบลงทะเบียนปิดให้บริการชั่วคราว\nโปรดลองใหม่อีกครั้ง")
        )
        return

    text = event.message.text
    user_id = event.source.user_id

    lines = text.strip().splitlines()
    if len(lines) != 6:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="❌ ต้องกรอกข้อมูล 6 บรรทัดเท่านั้น:\nชื่อ:\nชื่อเล่น:\nสาขา:\nตำแหน่ง:\nเริ่มงาน (DD-MM-YYYY):\nประเภท:")
        )
        return

    expected_keys = {"ชื่อ", "ชื่อเล่น", "สาขา", "ตำแหน่ง", "เริ่มงาน", "ประเภท"}
    data = {}
    for line in lines:
        if ":" not in line:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❌ ทุกบรรทัดต้องมีเครื่องหมาย ':' เช่น ตำแหน่ง: เจ้าหน้าที")
            )
            return
        key, val = line.split(":", 1)
        data[key.strip()] = val.strip()

    if set(data.keys()) != expected_keys:
        missing = expected_keys - set(data.keys())
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"❌ ขาดข้อมูล: {', '.join(missing)}")
        )
        return

    if not re.match(r'^\d{1,2}-\d{1,2}-\d{4}$', data["เริ่มงาน"]):
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="❌ รูปแบบวันเริ่มงานไม่ถูกต้อง (DD-MM-YYYY)")
        )
        return

    try:
        name, nickname = data["ชื่อ"], data["ชื่อเล่น"]
        branch, postion, start = data["สาขา"], data["ตำแหน่ง"], data["เริ่มงาน"]
        emp_type = data["ประเภท"].strip().lower()

        worksheet = client.open(spreadsheet_name).worksheet("DailyEmployee" if emp_type == "รายวัน" else "MonthlyEmployee")
        last_row = worksheet.get_all_values()[-1] if len(worksheet.get_all_values()) > 1 else []
        raw_code = last_row[2] if len(last_row) >= 3 else ""
        number_part = int(re.sub(r'\D', '', raw_code)) if raw_code.isdigit() or raw_code else default_code

        new_code = number_part + 1
        emp_code = prefix + str(new_code)

        now = datetime.now(pytz.timezone('Asia/Bangkok')).strftime("%d/%m/%Y %H:%M")

        worksheet.append_row(["", branch, emp_code, name, nickname, postion, start, "", emp_type, user_id, now])

        webhook_url = os.getenv(webhook_env_var)
        if webhook_url:
            requests.post(webhook_url, json={"sheet": worksheet.title})

        confirm_text = (
            f"✅ ลงทะเบียนสำเร็จ\n"
            f"รหัส: {emp_code}\n"
            f"ชื่อ: {name}\n"
            f"ตำแหน่ง: {postion}\n"
            f"สาขา: {branch}\n"
            f"เริ่มงาน: {start}\n"
            f"📌 โปรดแจ้งหัวหน้างาน/พนักงาน ล่วงหน้าก่อเริ่มงาน"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=confirm_text))

    except Exception as e:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"เกิดข้อผิดพลาด: {str(e)}")
        )

# === Bot 1 ===
LINE_CHANNEL_ACCESS_TOKEN_1 = os.getenv("LINE_CHANNEL_ACCESS_TOKEN_1")
LINE_CHANNEL_SECRET_1 = os.getenv("LINE_CHANNEL_SECRET_1")
line_bot_api1 = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN_1)
handler1 = WebhookHandler(LINE_CHANNEL_SECRET_1)

@app.route("/callback1", methods=['POST'])
def callback1():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message1(event):
    register_employee(event, line_bot_api1, "HR_EmployeeList", "APPS_SCRIPT_WEBHOOK1", default_code=90000)

# === Bot 2 ===
LINE_CHANNEL_ACCESS_TOKEN_2 = os.getenv("LINE_CHANNEL_ACCESS_TOKEN_2")
LINE_CHANNEL_SECRET_2 = os.getenv("LINE_CHANNEL_SECRET_2")
line_bot_api2 = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN_2)
handler2 = WebhookHandler(LINE_CHANNEL_SECRET_2)

@app.route("/callback2", methods=['POST'])
def callback2():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler2.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler2.add(MessageEvent, message=TextMessage)
def handle_message2(event):
    text = event.message.text.lower()
    is_daily = "รายวัน" in text
    register_employee(
        event,
        line_bot_api2,
        "HR_EmployeeListMikka",
        "APPS_SCRIPT_WEBHOOK2",
        default_code=20000 if is_daily else 60000,
        prefix="P" if is_daily else ""
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
