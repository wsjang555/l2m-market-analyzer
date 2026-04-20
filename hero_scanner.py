import asyncio
import aiohttp
import json
import time
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

api_key = "eyJraWQiOiI0OGEzNzliNS1mNGIxLTQ2Y2ItYTk4Zi0xOWNmM2VjOTEyYTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOiIwM0YxN0Y3NS1BM0E4LUUwMTEtQjlBOS1FNjFGMTM1RTk5MkYifQ.LN6qBKk0AgK-LY9j1apQXvq9BjeZMgUFHNMWz1eOizSlzn2HG2bl2r3reL6XVIEyPqTUknE4iy9UQvy3xWjKe7MENEvAJKjm3t7gPCQ-yjiq9p9kvI1GL-8vW57OTVOqPLHehogY4eZ7MeFex_UpaE3X1RHQchHSpyg1ZDe7oNqwsd6hg2CZ9brU0fhJHzwcVrqgc4aUZyEn7XotdN8fgN5I1Wq0VsZTW7ThL5N0262g2GtakFSmsm8fOdhEo6FM8r26aZ9uxr_t1dBQbgpPfOwf3rzGJttmydlI143u37Va6w1XbZLN96f-gaPE6s0PGeF_-U3E-RSAxcr1Kcd7OQ"
headers = {"Authorization": f"Bearer {api_key}"}

SEARCH_URL = "https://dev-api.plaync.com/l2m/v1.0/market/items/search"
PRICE_URL  = "https://dev-api.plaync.com/l2m/v1.0/market/items/{}/price"

SERVER_ID  = 1211  # 데스나이트 서버

# ============================================================
# 영웅(빨간색) 등급 무기 목록
# grade 값은 API 검색으로 확인 후 자동 감지
# ============================================================
HERO_WEAPON_NAMES = [
    # 한손검
    "아르카나 소드", "다마스커스", "아바돈 소드", "포가튼 블레이드",
    "크림슨 소드", "칼라드볼그", "나이트 소드",
    # 이도류
    "아스타로트", "아크엔젤 듀얼 소드", "탈룸 듀얼 소드", "다크 레기온",
    "테미스의 혀", "거인의 듀얼 소드", "다마스커스 듀얼 소드", "카리브스 듀얼 소드",
    "미혹의 듀얼 소드", "극한의 듀얼 소드", "실레노스 듀얼 소드",
    # 단검
    "나가스톰", "아크엔젤 슬레이어", "크루마의 뿔", "악마의 단검",
    "거인의 단검", "크리스", "헬나이프", "실레노스 대거",
    # 활
    "가스트라페테스", "실레노스 보우",
    # 지팡이
    "스타카토 퀸의 지팡이", "세계수의 가지", "데스페리온의 지팡이",
    "거인의 지팡이", "크리스탈 지팡이", "사령의 지팡이", "실레노스 스태프",
    # 오브
    "아르카나 오브", "아크엔젤 오브", "드래곤 플레임 헤드", "핸드 오브 카브리오",
    "거인의 오브", "스펠 브레이커", "이클립스 오브", "실레노스 오브",
    # 창
    "안타라스 스토머", "세인트 스피어", "타이폰 스피어", "탈룸 글레이브",
    "렌시아", "아크엔젤 핼버드", "핼버드", "아스칼론", "바디슬래셔",
    "거인의 창", "위도우메이커", "스콜피언", "사이드", "백금족 수호기사의 창",
    "하거인 수호 전사의 창",
    # 대검
    "발라카스 디바이더", "페더아이 버스터", "라바몬트 쏘우", "카오스 브레이커",
    "아크엔젤 버스터", "헤븐즈 윙블레이드", "쯔바이 핸더",
    "소드 오브 파아그리오", "하거인의 대검", "천궁 수호기사의 대검",
    "하거인 수호 전사의 대검",
    # 석궁
    "린드비오르 슈트제", "루드커터 크로스보우", "사룽가", "다이너스티 크로스보우",
    "쏜 크로스보우", "둠 싱어", "아크엔젤 크로스보우", "헬 하운드", "거인의 석궁",
    "피스메이커", "타스람",
]

# ============================================================
# 영웅(빨간색) 등급 방어구 목록
# ============================================================
HERO_ARMOR_NAMES = [
    # 투구
    "임페리얼 크루세이더 헬멧", "메이저 아르카나 서클릿", "드라코닉 레더 헬멧",
    "악몽의 투구", "다크 크리스탈 헬멧", "마제스틱 서클릿", "메두사의 투구",
    "둠 서클릿", "풀 플레이트 헬멧", "푸른 늑대의 헬멧", "파열의 투구",
    "엘븐 미스릴 투구", "미스릴 헬멧",
    # 상의
    "임페리얼 크루세이더 흉갑", "메이저 아르카나 로브", "드라코닉 레더 아머",
    "악몽의 갑옷", "다크 크리스탈 흉갑", "쉬르노엔의 흉갑", "아바돈 로브",
    "풀 플레이트 아머", "미스릴 흉갑", "엘븐 미스릴 흉갑", "컴포짓 아머",
    "씨커 레더 메일", "카르미안 튜닉",
    # 하의
    "풀 플레이트 각반", "바실라의 껍질", "언더월드 각반",
    "현자의 염령 호즈", "현자의 빙령 호즈", "현자의 풍령 호즈",
    "현자의 암령 호즈", "현자의 악령 호즈", "현자의 성령 호즈",
    # 장갑
    "임페리얼 크루세이더 건틀렛", "메이저 아르카나 글로브", "드라코닉 레더 글로브",
    "악몽의 건틀렛", "다크 크리스탈 글로브", "마제스틱 장갑", "푸른 늑대의 장갑",
    "풀 플레이트 건틀렛", "드레이크 레더 글로브", "파아그리오 핸드",
    "라인드 레더 글로브", "지식의 에바 글로브",
    # 부츠
    "임페리얼 크루세이더 부츠", "메이저 아르카나 부츠", "드라코닉 레더 부츠",
    "악마의 부츠", "다크 크리스탈 부츠", "마제스틱 부츠", "둠 부츠",
    "아바돈 부츠", "푸른 늑대의 부츠", "풀 플레이트 부츠", "미스릴 부츠",
    # 망토
    "샐러맨더 망토", "운디네 망토", "실리드 망토", "노움 망토",
    # 견갑
    "에파울렛 오브 피닉스", "에파울렛 오브 더 블러드",
]

# -----------------------------------------------------------
# 영웅 등급 grade 번호 자동 감지
# -----------------------------------------------------------
async def detect_hero_grade(session, sample_names):
    """샘플 아이템으로 API 응답 grade 번호를 자동 감지"""
    grade_counter = {}
    for name in sample_names[:5]:
        query = {"search_keyword": name, "sale": "true", "size": 5}
        try:
            async with session.get(SEARCH_URL, headers=headers, params=query, timeout=15) as res:
                if res.status == 200:
                    data = await res.json()
                    for item in data.get('contents', []):
                        if item.get('item_name') == name:
                            g = item.get('grade')
                            if g is not None:
                                grade_counter[g] = grade_counter.get(g, 0) + 1
                            break
        except Exception:
            pass
        await asyncio.sleep(0.1)
    if grade_counter:
        best = max(grade_counter, key=grade_counter.get)
        print(f"  >> 감지된 등급 코드: {best} (빈도:{grade_counter})")
        return best
    return None

# -----------------------------------------------------------
# 아이템 ID 조회 (grade 기준 없이 이름 일치 우선)
# -----------------------------------------------------------
async def fetch_item_by_name(session, name, target_grade):
    query = {"search_keyword": name, "sale": "true", "size": 10}
    try:
        async with session.get(SEARCH_URL, headers=headers, params=query, timeout=15) as res:
            if res.status == 200:
                data = await res.json()
                for item in data.get('contents', []):
                    if item.get('item_name') == name:
                        g = item.get('grade')
                        if target_grade is None or g == target_grade:
                            return (item.get('item_id'), name, g)
    except Exception as e:
        print(f"  검색 오류 ({name}): {e}")
    return None

# -----------------------------------------------------------
# 가격 조회
# -----------------------------------------------------------
async def get_price(session, item_id, name, enchant_level, server_id=SERVER_ID):
    url = PRICE_URL.format(item_id)
    try:
        async with session.get(url, headers=headers,
                               params={"server_id": server_id, "enchant_level": enchant_level},
                               timeout=10) as res:
            if res.status == 200:
                data = await res.json()
                price = data.get('now', {}).get('unit_price')
                return {"id": item_id, "name": name, "price": price}
    except Exception:
        pass
    return {"id": item_id, "name": name, "price": None}

# -----------------------------------------------------------
# 공통 스캐너 (무기 or 방어구)
# -----------------------------------------------------------
async def run_hero_scanner(item_type: str, item_names: list, high_enchant: int,
                           db_file: str, server_id=SERVER_ID):
    print(f"\n{'='*55}")
    print(f"  영웅(빨간색) {item_type} | 0강 vs +{high_enchant}강 차이 Top5")
    print(f"{'='*55}")
    start_time = time.time()

    # 1) DB 캐시 또는 신규 생성
    unique_items = {}  # {item_id: name}
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            unique_items = json.load(f)
        print(f"[1] 로컬 DB 로드 완료: {len(unique_items)}개 ({db_file})")
    else:
        print(f"[1] 영웅 {item_type} DB 구축 중... ({len(item_names)}종 검색)")
        async with aiohttp.ClientSession() as session:
            # grade 자동 감지
            hero_grade = await detect_hero_grade(session, item_names)
            print(f"     영웅 grade 코드: {hero_grade}")

            for name in item_names:
                result = await fetch_item_by_name(session, name, hero_grade)
                if result:
                    i_id, i_name, i_grade = result
                    if i_id not in unique_items:
                        unique_items[i_id] = i_name
                        print(f"  ✓ {i_name} (ID:{i_id}, grade:{i_grade})")
                await asyncio.sleep(0.05)

        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(unique_items, f, ensure_ascii=False, indent=2)
        print(f"     -> DB 저장 완료: {len(unique_items)}개")

    if not unique_items:
        print("  검색된 아이템이 없습니다.")
        return []

    # 2) +0강 가격 병렬 스캔
    print(f"\n[2] {len(unique_items)}개 {item_type}의 +0강 가격 스캔 중...")
    conn = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [get_price(session, i_id, name, 0, server_id)
                 for i_id, name in unique_items.items()]
        p0_results = await asyncio.gather(*tasks)

    p0_valid = [r for r in p0_results if r["price"] is not None]
    print(f"     -> 0강 매물 있음: {len(p0_valid)}개")

    if not p0_valid:
        print("  0강 매물이 없습니다.")
        return []

    # 3) +X강 가격 병렬 스캔
    print(f"[3] +{high_enchant}강 가격 스캔 중...")
    conn2 = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=conn2) as session:
        tasks = [get_price(session, i['id'], i['name'], high_enchant, server_id)
                 for i in p0_valid]
        pX_results = await asyncio.gather(*tasks)

    # 4) 가격 차이 계산
    final_results = []
    for p0_item, pX_item in zip(p0_valid, pX_results):
        if pX_item["price"] and p0_item["price"]:
            diff = round(pX_item["price"] - p0_item["price"], 4)
            final_results.append({
                "name":    p0_item["name"],
                "p0":      p0_item["price"],
                f"p{high_enchant}": pX_item["price"],
                "diff":    diff,
            })

    # 차이 큰 순으로 정렬
    final_results.sort(key=lambda x: x["diff"], reverse=True)

    elapsed = time.time() - start_time
    print(f"\n[완료] {elapsed:.2f}초")
    print(f"\n{'★'*3} 영웅 {item_type} Top5 (0강 vs +{high_enchant}강 차이 기준) {'★'*3}")
    if not final_results:
        print("  조건을 만족하는 매물이 없습니다.")
    for i, r in enumerate(final_results[:5], 1):
        print(f"  {i}. {r['name']}")
        print(f"     0강: {r['p0']} dia  |  +{high_enchant}강: {r[f'p{high_enchant}']} dia  |  차이: +{r['diff']} dia")

    return final_results[:5]

# -----------------------------------------------------------
# 메인
# -----------------------------------------------------------
async def main():
    print("\n리니지2M 영웅(빨간색) 매물 분석기")
    print("서버: 데스나이트 (1211)")

    # 무기: 0강 vs 7강
    weapon_results = await run_hero_scanner(
        item_type="무기",
        item_names=HERO_WEAPON_NAMES,
        high_enchant=7,
        db_file="item_db_hero_weapons.json",
        server_id=SERVER_ID,
    )

    print()

    # 방어구: 0강 vs 5강
    armor_results = await run_hero_scanner(
        item_type="방어구",
        item_names=HERO_ARMOR_NAMES,
        high_enchant=5,
        db_file="item_db_hero_armors.json",
        server_id=SERVER_ID,
    )

    print("\n\n===== 최종 요약 =====")
    print(f"\n[무기 Top5] 0강 vs +7강 차이")
    for i, r in enumerate(weapon_results, 1):
        print(f"  {i}. {r['name']} | 차이: +{r['diff']} 다이아 (0강:{r['p0']} → +7강:{r['p7']})")

    print(f"\n[방어구 Top5] 0강 vs +5강 차이")
    for i, r in enumerate(armor_results, 1):
        print(f"  {i}. {r['name']} | 차이: +{r['diff']} 다이아 (0강:{r['p0']} → +5강:{r['p5']})")

if __name__ == "__main__":
    asyncio.run(main())
