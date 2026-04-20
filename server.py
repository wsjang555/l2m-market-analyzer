import asyncio
import time
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from fast_l2m_scanner import run_fast_scanner as scan_w
from fast_armor_scanner import run_fast_armor_scanner as scan_a

load_dotenv()

app = FastAPI(title="L2M Dashboard API")

@app.get("/api/scan")
async def perform_full_scan():
    start_time = time.time()

    # ── 등급 정의 ──────────────────────────────────────────────
    # grade=1 : 일반(하얀색)
    # grade=2 : 고급(초록색)
    # grade=3 : 희귀(파란색)
    # ──────────────────────────────────────────────────────────

    # 3개 등급 병렬 스캔
    results = await asyncio.gather(
        scan_w(1, 9999.0, 7),   # 하얀색 무기 +7강
        scan_w(2, 9999.0, 7),   # 초록색 무기 +7강
        scan_w(3, 9999.0, 7),   # 파란색 무기 +7강
        scan_a(1, 9999.0, 5),   # 하얀색 방어구 +5강
        scan_a(2, 9999.0, 5),   # 초록색 방어구 +5강
        scan_a(3, 9999.0, 5),   # 파란색 방어구 +5강
        return_exceptions=True
    )

    def safe(r):
        return r if isinstance(r, list) else []

    total_time = round(time.time() - start_time, 2)

    return JSONResponse(content={
        "time": total_time,
        "weapon_level": 7,
        "armor_level": 5,
        "white_weapons":  safe(results[0]),
        "green_weapons":  safe(results[1]),
        "blue_weapons":   safe(results[2]),
        "white_armors":   safe(results[3]),
        "green_armors":   safe(results[4]),
        "blue_armors":    safe(results[5]),
    })


@app.post("/api/reset_cache")
async def reset_cache():
    deleted_files = []
    for f in os.listdir("."):
        if f.startswith("item_db_") and f.endswith(".json"):
            os.remove(f)
            deleted_files.append(f)
    return {"message": "Cache cleared.", "files": deleted_files}


# 정적 파일은 마지막에 마운트
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8080, reload=False)
