from flask import Flask
import threading
import os
import requests
from bs4 import BeautifulSoup
import time
import datetime
import re

# ============ 設定 ============
DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1376952972210208798/q468H-LKCXOyZBrThDN5ZeZyNUwAAl7y9fRzL_EwchS96403JHVS_GEsR5cgVklOe_bP"
TICKET_URL = "https://tixcraft.com/ticket/area/25_hyeri/19618"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ============ 假 Flask Server for Render ============
app = Flask(__name__)

@app.route('/')
def home():
    return "TixCraft bot is running 🎟️"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ============ 發送 Discord Embed ============
def send_to_discord_embed(title, description, url):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "embeds": [
            {
                "title": title,
                "description": f"{description}\n🕓 **通知時間：{now}**",
                "url": url,
                "color": 0x00cc66
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(DISCORD_WEBHOOK, json=data, headers=headers)
    if res.status_code in [200, 204]:
        print("✅ 通知已發送")
    else:
        print(f"❌ 通知失敗：{res.status_code} | {res.text}")

# ============ 票區掃描 ============
def check_ticket_page():
    try:
        res = requests.get(TICKET_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        font_tags = soup.select("li font")
        results = []

        if not font_tags:
            print(f"⚠️ 找不到票區標籤 ➜ {TICKET_URL}")
            return

        for tag in font_tags:
            text = tag.get_text(strip=True)
            print(f"🎫 {text}")
            if re.search(r"(剩餘|尚有|可售)", text):
                results.append(f"🎟️ {text}")

        if results:
            all_text = "\n".join(results)
            send_to_discord_embed("🎉 2025 HYERI FANMEETING TOUR", all_text, TICKET_URL)
        else:
            print(f"❌ 無票 ➜ {TICKET_URL}")

    except Exception as e:
        print(f"⚠️ 錯誤：{e}")

# ============ 主程式 ============
def run_bot():
    while True:
        check_ticket_page()
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
