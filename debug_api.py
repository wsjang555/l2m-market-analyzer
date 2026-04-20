import asyncio
import aiohttp
import json
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

api_key = "eyJraWQiOiI0OGEzNzliNS1mNGIxLTQ2Y2ItYTk4Zi0xOWNmM2VjOTEyYTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOiIwM0YxN0Y3NS1BM0E4LUUwMTEtQjlBOS1FNjFGMTM1RTk5MkYifQ.LN6qBKk0AgK-LY9j1apQXvq9BjeZMgUFHNMWz1eOizSlzn2HG2bl2r3reL6XVIEyPqTUknE4iy9UQvy3xWjKe7MENEvAJKjm3t7gPCQ-yjiq9p9kvI1GL-8vW57OTVOqPLHehogY4eZ7MeFex_UpaE3X1RHQchHSpyg1ZDe7oNqwsd6hg2CZ9brU0fhJHzwcVrqgc4aUZyEn7XotdN8fgN5I1Wq0VsZTW7ThL5N0262g2GtakFSmsm8fOdhEo6FM8r26aZ9uxr_t1dBQbgpPfOwf3rzGJttmydlI143u37Va6w1XbZLN96f-gaPE6s0PGeF_-U3E-RSAxcr1Kcd7OQ"
headers = {"Authorization": f"Bearer {api_key}"}

SEARCH_URL = "https://dev-api.plaync.com/l2m/v1.0/market/items/search"
PRICE_URL  = "https://dev-api.plaync.com/l2m/v1.0/market/items/{}/price"
SERVER_ID  = 1211

# 직접 게임에서 확인되는 아이템 몇 개 테스트
TEST_ITEMS = ["배크 드 코르뱅", "하거인 수호 전사의 창", "크림슨 소드", "임페리얼 크루세이더 헬멧"]

async def main():
    async with aiohttp.ClientSession() as session:
        for name in TEST_ITEMS:
            print(f"\n=== [{name}] 검색 결과 ===")
            query = {"search_keyword": name, "sale": "true", "size": 10}
            async with session.get(SEARCH_URL, headers=headers, params=query, timeout=15) as res:
                print(f"  HTTP 상태: {res.status}")
                if res.status == 200:
                    data = await res.json()
                    contents = data.get('contents', [])
                    print(f"  결과 수: {len(contents)}")
                    for item in contents:
                        print(f"  - 이름:{item.get('item_name')} | grade:{item.get('grade')} | item_id:{item.get('item_id')}")
                        item_id = item.get('item_id')
                        if item_id:
                            # 각 강화 단계별 가격 조회
                            for enchant in [0, 3, 5, 7]:
                                async with session.get(
                                    PRICE_URL.format(item_id), headers=headers,
                                    params={"server_id": SERVER_ID, "enchant_level": enchant},
                                    timeout=10
                                ) as price_res:
                                    if price_res.status == 200:
                                        pd = await price_res.json()
                                        now_price = pd.get('now', {}).get('unit_price')
                                        if now_price:
                                            print(f"      +{enchant}강 현재가: {now_price} 다이아")

asyncio.run(main())
