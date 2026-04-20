import asyncio
import time
import sys
import hmac
import hashlib
import secrets
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, Response, RedirectResponse, FileResponse
import os
from dotenv import load_dotenv

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from fast_l2m_scanner import run_fast_scanner as scan_w
from fast_armor_scanner import run_fast_armor_scanner as scan_a

load_dotenv()

app = FastAPI(title="L2M Dashboard API")

# ── 쿠키 세션 토큰 생성/검증 ────────────────────────────────────
def _make_token(username: str, password: str) -> str:
    secret = os.getenv("SECRET_KEY", "l2m-default-secret-key-change-me")
    msg = f"{username}:{password}"
    return hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()

def _verify_session(token: str) -> bool:
    username = os.getenv("APP_USERNAME", "admin")
    password = os.getenv("APP_PASSWORD", "l2m2024!")
    expected = _make_token(username, password)
    return secrets.compare_digest(token, expected)
# ────────────────────────────────────────────────────────────────

# ── 인증 미들웨어: 로그인 페이지/엔드포인트만 허용, 나머지는 쿠키 확인
WHITELIST = {"/login", "/auth/login"}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path in WHITELIST:
        return await call_next(request)

    session_token = request.cookies.get("l2m_session", "")
    if _verify_session(session_token):
        return await call_next(request)

    # 미인증 → 로그인 페이지로 리다이렉트
    return RedirectResponse(url="/login", status_code=302)
# ────────────────────────────────────────────────────────────────

# ── 로그인 페이지 ────────────────────────────────────────────────
@app.get("/login")
async def login_page(error: int = 0):
    return FileResponse("static/login.html")

@app.post("/auth/login")
async def do_login(
    username: str = Form(...),
    password: str = Form(...),
):
    correct_username = os.getenv("APP_USERNAME", "admin")
    correct_password = os.getenv("APP_PASSWORD", "l2m2024!")

    ok_user = secrets.compare_digest(username, correct_username)
    ok_pass = secrets.compare_digest(password, correct_password)

    if ok_user and ok_pass:
        token = _make_token(username, password)
        response = RedirectResponse(url="/", status_code=302)
        # 30일 유지 (httponly 쿠키 — JS에서 접근 불가)
        response.set_cookie(
            "l2m_session", token,
            httponly=True, max_age=86400 * 30, samesite="lax"
        )
        return response

    # 실패 → 로그인 페이지로 돌아감 (error 파라미터)
    return RedirectResponse(url="/login?error=1", status_code=302)

@app.get("/auth/logout")
async def do_logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("l2m_session")
    return response
# ────────────────────────────────────────────────────────────────

@app.get("/api/scan")
async def perform_full_scan():
    start_time = time.time()

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
