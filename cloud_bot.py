import asyncio
import os
import time
import urllib.parse
from dotenv import load_dotenv
import aiohttp

# 리니지2M 스캐너 임포트
from fast_l2m_scanner import run_fast_scanner as scan_w
from fast_armor_scanner import run_fast_armor_scanner as scan_a

# .env 파일에서 환경변수 로딩
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
SCAN_INTERVAL_MINUTES = int(os.getenv("SCAN_INTERVAL_MINUTES", "60"))

# 결과 데이터를 텔레그램 포맷 문자열로 변환하는 함수
def format_results(title, results, pX_level):
    msg = f"<b>{title}</b>\n"
    if not results:
        msg += " - 조건을 만족하는 매물이 없습니다.\n\n"
        return msg
    
    for i, r in enumerate(results):
        msg += f"{i+1}. {r['name']} (+{pX_level}): {r[f'p{pX_level}']} 다이아\n"
    msg += "\n"
    return msg

async def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("❗ Telegram Token 또는 Chat ID가 설정되지 않아 로컬에만 출력됩니다.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    print(f"텔레그램 발송 실패: {await response.text()}")
    except Exception as e:
        print(f"텔레그램 발송 중 에러 발생: {e}")

async def fetch_and_alert():
    print(f"\n[알림봇 작동 시작] {time.strftime('%Y-%m-%d %H:%M:%S')}")
    full_message = "🔔 <b>리니지2M 꿀매물 스캔 타임!</b> 🔔\n\n"

    try:
        # 1. 하얀색 무기, 0강 10다이아, 7강
        res1 = await scan_w(1, 10.0, 7)
        full_message += format_results("1️⃣ 하얀색무기(일반) +7강 최고가", res1, 7)

        # 2. 녹색 무기, 0강 10다이아, 7강
        res2 = await scan_w(2, 10.0, 7)
        full_message += format_results("2️⃣ 녹색무기(고급) +7강 최고가", res2, 7)

        # 3. 하얀색 방어구, 0강 10다이아, 5강
        res3 = await scan_a(1, 10.0, 5)
        full_message += format_results("3️⃣ 하얀색방어구(일반) +5강 최고가", res3, 5)

        # 4. 녹색 방어구, 0강 10다이아, 5강
        res4 = await scan_a(2, 10.0, 5)
        full_message += format_results("4️⃣ 녹색방어구(고급) +5강 최고가", res4, 5)

        # 5. 하얀색 무기, 0강 10다이아, 8강
        res5 = await scan_w(1, 10.0, 8)
        full_message += format_results("5️⃣ 하얀색무기(일반) +8강 최고가", res5, 8)

        # 6. 녹색 무기, 0강 10다이아, 8강
        res6 = await scan_w(2, 10.0, 8)
        full_message += format_results("6️⃣ 녹색무기(고급) +8강 최고가", res6, 8)

        # 7. 하얀색 방어구, 0강 10다이아, 6강
        res7 = await scan_a(1, 10.0, 6)
        full_message += format_results("7️⃣ 하얀색방어구(일반) +6강 최고가", res7, 6)

        # 8. 녹색 방어구, 0강 10다이아, 6강
        res8 = await scan_a(2, 10.0, 6)
        full_message += format_results("8️⃣ 녹색방어구(고급) +6강 최고가", res8, 6)

        # 텔레그램으로 텍스트 발송
        await send_telegram_message(full_message)
        print("✅ 텔레그램 알림 발송 완료!")

    except Exception as e:
        print(f"스캔 중 에러 발생: {e}")

async def main_loop():
    print("🤖 리니지2M 클라우드 알림 봇 가동!")
    print(f"⏱️ 설정된 스캔 주기: {SCAN_INTERVAL_MINUTES}분")
    
    while True:
        await fetch_and_alert()
        
        # 다음 스캔까지 대기
        wait_seconds = SCAN_INTERVAL_MINUTES * 60
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] 다음 스캔까지 {SCAN_INTERVAL_MINUTES}분 대기합니다...")
        await asyncio.sleep(wait_seconds)

if __name__ == '__main__':
    asyncio.run(main_loop())
