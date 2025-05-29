from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
import datetime
import re

DISCORD_WEBHOOK = "https://discordapp.com/api/webhooks/1376952972210208798/q468H-LKCXOyZBrThDN5ZeZyNUwAAl7y9fRzL_EwchS96403JHVS_GEsR5cgVklOe_bP"

CHROMEDRIVER_PATH = r"C:\ticket_bot\chromedriver.exe"

TICKET_URL = "https://tixcraft.com/ticket/area/25_hyeri/19618"


options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)

# 發送 Discord Embed
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
        print(f"❌ 發送失敗：{res.status_code} | {res.text}")

# 檢查這一頁的票區
def check_ticket_page():
    driver.get(TICKET_URL)
    time.sleep(3)

    try:
        links = driver.find_elements(By.CSS_SELECTOR, "li.select_form_b > a[style*='opacity: 1']")
        results = []

        for link in links:
            text = link.text.strip().replace("\n", " ")
            print(f"🎫 {text}")

            match = re.search(r"剩餘\s*(\d+)", text)
            if match and int(match.group(1)) > 0:
                results.append(f"🎟️ {text}")

        if results:
            msg = "\n".join(results)
            send_to_discord_embed(
                title="🎉 2025 HYERI FANMEETING TOUR",
                description=msg,
                url=TICKET_URL
            )
        else:
            print("❌ 無票：目前無任何可售票")

    except Exception as e:
        print("⚠️ 錯誤：", str(e))

# 持續掃描
while True:
    check_ticket_page()
    time.sleep(60)