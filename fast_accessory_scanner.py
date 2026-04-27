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
PRICE_URL  = "https://dev-api.plaync.com/l2m/v1.0/market/items/{}/price"

# ============================================================
# 키워드 기반 장신구 자동 탐색 (이름 하드코딩 불필요)
# API에서 grade == target_grade 인 item만 수집
# ============================================================
ACCESSORY_KEYWORDS = [
    "이어링", "귀걸이", "네클리스", "네크리스", "목걸이",
    "반지", "링", "팔찌", "브레이슬릿", "아뮬렛",
    "오브", "클러치", "브로치",
]

ITEM_DB_FILE = "item_db_accessories_{}.json"  # 등급별 캐싱


async def fetch_all_items(target_grade):
    """
    키워드 탐색 방식으로 거래소에 등록된 grade==target_grade 장신구를 자동 수집.
    이름 하드코딩 없이 API 응답에서 직접 grade 필터링.
    """
    print(f"1) 장신구(등급:{target_grade}) DB 구축 중... (키워드 자동 탐색: {len(ACCESSORY_KEYWORDS)}개 키워드)")
    unique_items = {}
    async with aiohttp.ClientSession() as session:
        for keyword in ACCESSORY_KEYWORDS:
            query = {"search_keyword": keyword, "sale": "true", "size": 50}
            try:
                async with session.get(SEARCH_URL, headers=headers, params=query, timeout=15) as res:
                    if res.status == 200:
                        data = await res.json()
                        for item in data.get('contents', []):
                            if item.get('grade') == target_grade:
                                i_id = str(item.get('item_id'))
                                i_name = item.get('item_name')
                                if i_id not in unique_items:
                                    unique_items[i_id] = i_name
                                    print(f"  ✓ [{target_grade}등급] {i_name} (ID:{i_id})")
            except Exception as e:
                print(f"  탐색 오류 ({keyword}): {e}")
            await asyncio.sleep(0.15)

    db_filename = ITEM_DB_FILE.format(target_grade)
    with open(db_filename, 'w', encoding='utf-8') as f:
        json.dump(unique_items, f, ensure_ascii=False, indent=2)
    print(f" -> 로컬 DB 저장 완료: {len(unique_items)}개의 장신구 확보")
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


async def run_accessory_scanner(target_grade, top_n=3, server_id=1211):
    """
    파란색(희귀) 장신구 중 0강 가격이 가장 저렴한 top_n개를 반환.
    """
    print(f"\n[장신구 스캐너] 등급:{target_grade}, 0강 최저가 Top{top_n} 기준")
    start_time = time.time()

    unique_items = {}
    db_filename = ITEM_DB_FILE.format(target_grade)

    if os.path.exists(db_filename):
        with open(db_filename, 'r', encoding='utf-8') as f:
            unique_items = json.load(f)
        print(f"1) 로컬 DB 로드 완료: {len(unique_items)}개의 장신구 확보 (캐시 사용)")
    else:
        unique_items = await fetch_all_items(target_grade)

    if not unique_items:
        print("검색된 장신구가 없습니다.")
        return []

    # 0강 가격 병렬 스캔
    print(f"2) {len(unique_items)}개 장신구의 0강 실시간 가격 전수 스캔 중...")
    conn = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [get_price(session, i_id, name, 0, server_id) for i_id, name in unique_items.items()]
        results = await asyncio.gather(*tasks)

    # 가격이 존재하는 것만 필터링 후 오름차순 정렬 (가장 싼 것 우선)
    priced = [r for r in results if r["price"] is not None]
    priced.sort(key=lambda x: x["price"])

    final_results = []
    for item in priced[:top_n]:
        final_results.append({
            "name": item["name"],
            "p0": item["price"],
        })

    end_time = time.time()
    print(f"\n[완료] 스캔 완료! ({end_time - start_time:.2f}초)")
    print(f"\n[Top{top_n}] 장신구 0강 최저가:")
    for r in final_results:
        print(f"  - {r['name']} | 0강:{r['p0']} 다이아")

    return final_results


if __name__ == "__main__":
    asyncio.run(run_accessory_scanner(target_grade=3, top_n=3, server_id=1211))
