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

# ============================================================
# 시길 아이템 전체 목록
# ============================================================
ALL_SIGIL_NAMES = [
    "티어 오브 다크니스",
    "자이브의 시길",
    "스피릿 시길",
    "불사조의 명예",
    "기사단의 명예",
    "수장 가문 시길",
    "오키쉬 시길",
    "청동 시길",
    "철 시길",
    "나무 시길",
]

ITEM_DB_FILE = "item_db_sigils_{}.json"  # 등급별 캐싱


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


async def fetch_all_sigils(target_grade):
    print(f"1) 시길(등급:{target_grade}) DB 구축 중... ({len(ALL_SIGIL_NAMES)}종 검색)")
    unique_items = {}
    async with aiohttp.ClientSession() as session:
        for name in ALL_SIGIL_NAMES:
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
    print(f" -> 로컬 DB 저장 완료: {len(unique_items)}개 시길 확보")
    return unique_items


async def get_price(session, item_id, name, enchant_level, server_id=1211):
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


async def run_sigil_scanner(target_grade, pX_level, server_id=1211):
    """
    해당 등급 시길 중 0강↔pX강 가격 차이가 가장 큰 Top3 반환.
    """
    print(f"\n[시길 스캐너] 등급:{target_grade}, 0강↔+{pX_level}강 차익 Top3")
    start_time = time.time()

    db_filename = ITEM_DB_FILE.format(target_grade)
    if os.path.exists(db_filename):
        with open(db_filename, 'r', encoding='utf-8') as f:
            unique_items = json.load(f)
        print(f"1) 로컬 DB 로드 완료: {len(unique_items)}개 시길 (캐시 사용)")
    else:
        unique_items = await fetch_all_sigils(target_grade)

    if not unique_items:
        print("검색된 시길이 없습니다.")
        return []

    # 0강 가격 전수 스캔
    print(f"2) {len(unique_items)}개 시길 0강 가격 스캔 중...")
    conn = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks_p0 = [get_price(session, i_id, name, 0, server_id)
                    for i_id, name in unique_items.items()]
        results_p0 = await asyncio.gather(*tasks_p0)

    candidates = [r for r in results_p0 if r["price"] is not None]

    if not candidates:
        print("  0강 매물 없음")
        return []

    # pX강 가격 스캔
    print(f"3) +{pX_level}강 가격 스캔 중...")
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
        tasks_pX = [get_price(session, c['id'], c['name'], pX_level, server_id)
                    for c in candidates]
        results_pX = await asyncio.gather(*tasks_pX)

    final_results = []
    for p0_item, pX_item in zip(candidates, results_pX):
        if pX_item["price"] and p0_item["price"]:
            diff = pX_item["price"] - p0_item["price"]
            final_results.append({
                "name":  p0_item["name"],
                "p0":    p0_item["price"],
                f"p{pX_level}": pX_item["price"],
                "diff":  round(diff, 4)
            })

    final_results.sort(key=lambda x: x['diff'], reverse=True)

    end_time = time.time()
    print(f"\n[완료] ({end_time - start_time:.2f}초)")
    print(f"\n[Top3] 시길 +{pX_level}강 차익순:")
    for r in final_results[:3]:
        print(f"  - {r['name']} | 0강:{r['p0']} -> +{pX_level}강:{r[f'p{pX_level}']} | 차이:{r['diff']} 다이아")

    return final_results[:3]


if __name__ == "__main__":
    asyncio.run(run_sigil_scanner(target_grade=3, pX_level=1, server_id=1211))
