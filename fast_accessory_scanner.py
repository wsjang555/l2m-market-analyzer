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
# 리니지2M 전체 장신구 이름 목록 (목걸이, 귀걸이, 반지)
# ============================================================
ALL_ACCESSORY_NAMES = [
    # 목걸이
    "코어 네클리스", "포가튼 네클리스", "이글 아이 네클리스", "쿼드 워크래프트 네클리스",
    "트리플 워크래프트 네클리스", "트리플 듀얼 네클리스", "쿼드 소울 로스트 네클리스",
    "쿼드 파이터즈 네클리스", "트리플 파이터즈 네클리스", "엘더 네클리스",
    "골드 네클리스", "믿음의 네클리스", "수호의 네클리스", "치유의 네클리스",
    "용기의 네클리스", "강철의 네클리스", "지혜의 네클리스", "행운의 목걸이",
    "은 목걸이", "청동 목걸이", "구리 목걸이", "철 목걸이",
    "마나의 목걸이", "생명의 목걸이", "힘의 목걸이",
    # 귀걸이
    "코어 이어링", "포가튼 이어링", "이글 아이 이어링", "쿼드 워크래프트 이어링",
    "트리플 워크래프트 이어링", "트리플 듀얼 이어링", "쿼드 파이터즈 이어링",
    "트리플 파이터즈 이어링", "엘더 이어링", "골드 이어링",
    "믿음의 귀걸이", "수호의 귀걸이", "치유의 귀걸이", "용기의 귀걸이",
    "강철의 귀걸이", "지혜의 귀걸이", "행운의 귀걸이", "은 귀걸이",
    "청동 귀걸이", "구리 귀걸이", "철 귀걸이",
    "마나의 귀걸이", "생명의 귀걸이", "힘의 귀걸이",
    # 반지
    "코어 링", "포가튼 링", "이글 아이 링", "쿼드 워크래프트 링",
    "트리플 워크래프트 링", "트리플 듀얼 링", "쿼드 파이터즈 링",
    "트리플 파이터즈 링", "엘더 링", "골드 링",
    "믿음의 반지", "수호의 반지", "치유의 반지", "용기의 반지",
    "강철의 반지", "지혜의 반지", "행운의 반지", "은 반지",
    "청동 반지", "구리 반지", "철 반지",
    "마나의 반지", "생명의 반지", "힘의 반지",
]

ITEM_DB_FILE = "item_db_accessories_{}.json"  # 등급별 캐싱


async def fetch_item_by_name(session, name, target_grade):
    """정확한 아이템 이름으로 단건 검색"""
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
    print(f"1) 장신구(등급:{target_grade}) 전체 목록 DB 구축 중... ({len(ALL_ACCESSORY_NAMES)}종 직접 검색)")
    unique_items = {}
    async with aiohttp.ClientSession() as session:
        for name in ALL_ACCESSORY_NAMES:
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
