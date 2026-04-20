import asyncio
import time
import sys
import base64
import secrets
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response
import os
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from fast_l2m_scanner import run_fast_scanner as scan_w
from fast_armor_scanner import run_fast_armor_scanner as scan_a

load_dotenv()

app = FastAPI(title="L2M Dashboard API")

# ── HTTP Basic Auth 미들웨어 ────────────────────────────────────
# Render 환경변수 APP_USERNAME, APP_PASSWORD 로 설정
# 미설정 시 기본값: admin / l2m1234
@app.middleware("http")
async def basic_auth_middleware(request: Request, call_next):
    app_username = os.getenv("APP_USERNAME", "admin")
    app_password = os.getenv("APP_PASSWORD", "l2m1234")

    auth_header = request.headers.get("Authorization", "")
    authorized = False

    if auth_header.startswith("Basic "):
        try:
            decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
            username, password = decoded.split(":", 1)
            ok_user = secrets.compare_digest(username, app_username)
            ok_pass = secrets.compare_digest(password, app_password)
            authorized = ok_user and ok_pass
        except Exception:
            pass

    if not authorized:
        return Response(
            content="접근 권한이 없습니다. 아이디와 비밀번호를 입력하세요.",
            status_code=401,
            headers={"WWW-Authenticate": 'Basic realm="L2M Dashboard"'},
        )

    return await call_next(request)
# ────────────────────────────────────────────────────────────────

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
