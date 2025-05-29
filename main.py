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

        li_tags = soup.select("li")
        results = []
        all_checked = []

        if not li_tags:
            print(f"⚠️ 找不到任何 <li> 元素 ➜ {TICKET_URL}")
            return

        for li in li_tags:
            text = li.get_text(strip=True).replace("\n", " ")
            if not text:
                continue
            all_checked.append(text)
            if re.search(r"(剩餘|尚有|可售)", text):
                results.append(f"🎟️ {text}")

        # === 有票 ===
        if results:
            all_text = "\n".join(results)
            send_to_discord_embed("🎉 有票啦！", all_text, TICKET_URL)

        # === 沒票（也顯示所有檢查過的區塊）===
        else:
            print(f"❌ 無票 ➜ {TICKET_URL}")
            print("🔍 掃描結果：")
            for zone in all_checked:
                print(f" - {zone}")

    except Exception as e:
        print(f"⚠️ 錯誤 ➜ {TICKET_URL}：{e}")


# ============ 主程式 ============
def run_bot():
    while True:
        check_ticket_page()
        time.sleep(60)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    run_bot()
