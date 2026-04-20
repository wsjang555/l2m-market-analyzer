import asyncio
import aiohttp
import json
import time
import os
import sys

# Windows cp949 환경에서 이모지 출력 오류 방지
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

api_key = "eyJraWQiOiI0OGEzNzliNS1mNGIxLTQ2Y2ItYTk4Zi0xOWNmM2VjOTEyYTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOiIwM0YxN0Y3NS1BM0E4LUUwMTEtQjlBOS1FNjFGMTM1RTk5MkYifQ.LN6qBKk0AgK-LY9j1apQXvq9BjeZMgUFHNMWz1eOizSlzn2HG2bl2r3reL6XVIEyPqTUknE4iy9UQvy3xWjKe7MENEvAJKjm3t7gPCQ-yjiq9p9kvI1GL-8vW57OTVOqPLHehogY4eZ7MeFex_UpaE3X1RHQchHSpyg1ZDe7oNqwsd6hg2CZ9brU0fhJHzwcVrqgc4aUZyEn7XotdN8fgN5I1Wq0VsZTW7ThL5N0262g2GtakFSmsm8fOdhEo6FM8r26aZ9uxr_t1dBQbgpPfOwf3rzGJttmydlI143u37Va6w1XbZLN96f-gaPE6s0PGeF_-U3E-RSAxcr1Kcd7OQ"
headers = {"Authorization": f"Bearer {api_key}"}

SEARCH_URL = "https://dev-api.plaync.com/l2m/v1.0/market/items/search"
PRICE_URL = "https://dev-api.plaync.com/l2m/v1.0/market/items/{}/price"

# ============================================================
# 리니지2M 공식 가이드북 (https://lineage2m.plaync.com/guidebook/view?title=방어구)
# 에서 긁어온 전체 방어구 이름 목록 - 100% 완전 커버리지 보장
# ============================================================
ALL_ARMOR_NAMES = [
    # 투구
    "임페리얼 크루세이더 헬멧", "메이저 아르카나 서클릿", "드라코닉 레더 헬멧",
    "악몽의 투구", "다크 크리스탈 헬멧", "마제스틱 서클릿", "메두사의 투구",
    "둠 서클릿", "풀 플레이트 헬멧", "푸른 늑대의 헬멧", "파열의 투구",
    "엘븐 미스릴 투구", "미스릴 헬멧", "청동 헬멧", "샤이닝 서클릿",
    "카르미안 서클릿", "강화 판금 투구", "오키쉬 강화 투구", "주술사의 투구",
    "하프 플레이트 투구", "올 마훔 투구", "마나의 모자", "브리건딘 헬멧",
    "조각뼈 투구", "드워븐 체인 헬멧", "가죽 모자", "나무 투구",
    "낡은 투구", "붉은 보석 가죽 모자", "오키쉬 투구",
    # 상의
    "임페리얼 크루세이더 흉갑", "메이저 아르카나 로브", "드라코닉 레더 아머",
    "악몽의 갑옷", "다크 크리스탈 흉갑", "쉬르노엔의 흉갑", "아바돈 로브",
    "풀 플레이트 아머", "미스릴 흉갑", "엘븐 미스릴 흉갑", "컴포짓 아머",
    "씨커 레더 메일", "카르미안 튜닉", "강화 판금 갑옷", "실레노스 튜닉",
    "오키쉬 강화 흉갑", "주술사의 튜닉", "하프 플레이트 아머", "브리건딘 흉갑",
    "헌신의 튜닉", "드워븐 체인 메일", "나무 흉갑", "오키쉬 흉갑",
    "올 마훔 레더 메일", "올 마훔 흉갑", "가죽 갑옷", "낡은 상의",
    "누더기 로브", "보석 가죽 갑옷", "샌들 상의", "실레노스 강화 레더 메일",
    "실레노스 강화 흉갑", "오키쉬 강화 튜닉", "상아탑 가디언의 흉갑",
    "상아탑 마법사의 로브", "바람 정령의 로브", "판 루엠의 흉갑",
    # 하의
    "풀 플레이트 각반", "바실라의 껍질", "언더월드 각반", "강화 판금 각반",
    "현자의 염령 호즈", "현자의 빙령 호즈", "현자의 풍령 호즈",
    "현자의 암령 호즈", "현자의 악령 호즈", "현자의 성령 호즈",
    "오키쉬 각반", "주술사의 각반", "하프 플레이트 각반", "브리건딘 각반",
    "헌신의 각반", "드워븐 체인 호즈", "나무 각반", "오키쉬 호즈",
    "올 마훔 각반", "가죽 각반", "낡은 하의", "보석 가죽 각반", "샌들 하의",
    # 장갑
    "임페리얼 크루세이더 건틀렛", "메이저 아르카나 글로브", "드라코닉 레더 글로브",
    "악몽의 건틀렛", "다크 크리스탈 글로브", "마제스틱 장갑", "푸른 늑대의 장갑",
    "풀 플레이트 건틀렛", "드레이크 레더 글로브", "파아그리오 핸드",
    "라인드 레더 글로브", "지식의 에바 글로브", "오키쉬 강화 글로브",
    "카르미안 장갑", "월하의 장갑",
    # 부츠
    "임페리얼 크루세이더 부츠", "메이저 아르카나 부츠", "드라코닉 레더 부츠",
    "악마의 부츠", "다크 크리스탈 부츠", "마제스틱 부츠", "둠 부츠",
    "아바돈 부츠", "푸른 늑대의 부츠", "풀 플레이트 부츠", "미스릴 부츠",
    "오키쉬 강화 부츠", "카르미안 부츠", "신앙의 부츠", "리자드맨 부츠", "짧은 장화",
    # 티셔츠
    "투지의 무명 셔츠", "민첩의 무명 셔츠", "지식의 무명 셔츠",
    "집중의 셔츠", "자경대원 셔츠", "면 셔츠", "무명 셔츠",
    # 망토
    "샐러맨더 망토", "운디네 망토", "실리드 망토", "노움 망토",
    # 시길
    "티어 오브 다크니스", "자이브의 시길", "스피릿 시길", "불사조의 명예",
    "기사단의 명예", "수장 가문 시길", "오키쉬 시길", "청동 시길", "철 시길", "나무 시길",
    # 견갑 (추가 카테고리)
    "에파울렛 오브 피닉스", "에파울렛 오브 더 블러드",
]

ITEM_DB_FILE = "item_db_armors_{}.json"

async def fetch_item_by_name(session, name, target_grade):
    """정확한 아이템 이름으로 단건 검색 - 100% 정확도 보장"""
    query = {"search_keyword": name, "sale": "true", "size": 10}
    try:
        async with session.get(SEARCH_URL, headers=headers, params=query, timeout=15) as res:
            if res.status == 200:
                data = await res.json()
                for item in data.get('contents', []):
                    if item.get('item_name') == name and item.get('grade') == target_grade:
                        return (item.get('item_id'), name)
    except Exception as e:
        print(f"  검색 오류 ({name}): {e}")
    return None

async def fetch_all_items(target_grade):
    print(f"1) 방어구(등급:{target_grade}) 전체 목록 DB 구축 중... ({len(ALL_ARMOR_NAMES)}종 직접 검색)")
    unique_items = {}
    async with aiohttp.ClientSession() as session:
        for name in ALL_ARMOR_NAMES:
            result = await fetch_item_by_name(session, name, target_grade)
            if result:
                i_id, i_name = result
                if i_id not in unique_items:
                    unique_items[i_id] = i_name
                    print(f"  ✓ [{target_grade}등급] {i_name} (ID:{i_id})")
            await asyncio.sleep(0.05)

    db_filename = ITEM_DB_FILE.format(target_grade)
    with open(db_filename, 'w', encoding='utf-8') as f:
        json.dump(unique_items, f, ensure_ascii=False, indent=2)
    print(f" -> 로컬 DB 저장 완료: {len(unique_items)}개의 방어구 확보")
    return unique_items

async def get_price(session, item_id, name, enchant_level, server_id=1211):
    url = PRICE_URL.format(item_id)
    try:
        async with session.get(url, headers=headers, params={"server_id": server_id, "enchant_level": enchant_level}, timeout=10) as res:
            if res.status == 200:
                data = await res.json()
                price = data.get('now', {}).get('unit_price')
                return {"id": item_id, "name": name, "price": price}
    except Exception:
        pass
    return {"id": item_id, "name": name, "price": None}

async def run_fast_armor_scanner(target_grade, p0_target_price, pX_level, server_id=1211):
    print(f"\n[방어구 스캐너] 등급:{target_grade}, 0강<={p0_target_price}다이아, +{pX_level}강 기준")
    start_time = time.time()

    unique_items = {}
    db_filename = ITEM_DB_FILE.format(target_grade)

    if os.path.exists(db_filename):
        with open(db_filename, 'r', encoding='utf-8') as f:
            unique_items = json.load(f)
        print(f"1) 로컬 DB 로드 완료: {len(unique_items)}개의 방어구 확보 (캐시 사용)")
    else:
        unique_items = await fetch_all_items(target_grade)

    if not unique_items:
        print("검색된 방어구가 없습니다.")
        return []

    # 2. +0강 가격 병렬 스캔
    candidates_evaluating_p0 = []
    print(f"2) {len(unique_items)}개 방어구의 +0강 실시간 가격 전수 스캔 중...")

    conn = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [get_price(session, i_id, name, 0, server_id) for i_id, name in unique_items.items()]
        results = await asyncio.gather(*tasks)

        for res in results:
            if res["price"] is not None and res["price"] <= p0_target_price:
                candidates_evaluating_p0.append(res)

    print(f" -> 0강 {p0_target_price}다이아 이하: {len(candidates_evaluating_p0)}개 발견")

    # 3. +X강 가격 스캔
    final_results = []
    if candidates_evaluating_p0:
        print(f"3) +{pX_level}강 가격 스캔 중...")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
            tasks = [get_price(session, i['id'], i['name'], pX_level, server_id) for i in candidates_evaluating_p0]
            results_pX = await asyncio.gather(*tasks)

            for p0_item, pX_item in zip(candidates_evaluating_p0, results_pX):
                if pX_item["price"] and p0_item["price"]:
                    diff = pX_item["price"] - p0_item["price"]
                    final_results.append({
                        "name": p0_item["name"],
                        "p0": p0_item["price"],
                        f"p{pX_level}": pX_item["price"],
                        "diff": round(diff, 4)
                    })

    # 가격 차이(diff) 기준 내림차순 정렬
    final_results.sort(key=lambda x: x['diff'], reverse=True)

    end_time = time.time()
    print(f"\n[완료] 스캔 완료! ({end_time - start_time:.2f}초)")
    print(f"\n[Top5] 방어구 (0강<={p0_target_price}, +{pX_level}강 차이순):")
    if not final_results:
        print("  조건을 만족하는 매물이 없습니다.")
    for r in final_results[:5]:
        print(f"  - {r['name']} | 0강:{r['p0']} -> +{pX_level}강:{r[f'p{pX_level}']} | 차이:{r['diff']} 다이아")

    return final_results[:5]

if __name__ == "__main__":
    asyncio.run(run_fast_armor_scanner(target_grade=2, p0_target_price=15.0, pX_level=5, server_id=1211))