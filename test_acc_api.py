import asyncio
import aiohttp
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

api_key = "eyJraWQiOiI0OGEzNzliNS1mNGIxLTQ2Y2ItYTk4Zi0xOWNmM2VjOTEyYTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOiIwM0YxN0Y3NS1BM0E4LUUwMTEtQjlBOS1FNjFGMTM1RTk5MkYifQ.LN6qBKk0AgK-LY9j1apQXvq9BjeZMgUFHNMWz1eOizSlzn2HG2bl2r3reL6XVIEyPqTUknE4iy9UQvy3xWjKe7MENEvAJKjm3t7gPCQ-yjiq9p9kvI1GL-8vW57OTVOqPLHehogY4eZ7MeFex_UpaE3X1RHQchHSpyg1ZDe7oNqwsd6hg2CZ9brU0fhJHzwcVrqgc4aUZyEn7XotdN8fgN5I1Wq0VsZTW7ThL5N0262g2GtakFSmsm8fOdhEo6FM8r26aZ9uxr_t1dBQbgpPfOwf3rzGJttmydlI143u37Va6w1XbZLN96f-gaPE6s0PGeF_-U3E-RSAxcr1Kcd7OQ"
headers = {"Authorization": f"Bearer {api_key}"}
SEARCH_URL = "https://dev-api.plaync.com/l2m/v1.0/market/items/search"

test_names = ["골드 네클리스", "믿음의 네클리스", "엘더 이어링", "골드 링", "코어 링", "은 반지", "행운의 목걸이"]

results = []

async def test():
    async with aiohttp.ClientSession() as session:
        for name in test_names:
            params = {"search_keyword": name, "sale": "true", "size": 10}
            async with session.get(SEARCH_URL, headers=headers, params=params, timeout=10) as res:
                data = await res.json()
                items = data.get("contents", [])
                line = f"[{name}] 결과 {len(items)}개:"
                results.append(line)
                for it in items:
                    grade = it.get("grade")
                    iname = it.get("item_name")
                    iid = it.get("item_id")
                    results.append(f"  grade={grade}, name={iname}, id={iid}")
            await asyncio.sleep(0.3)

    with open("acc_test_result.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(results))
    print("결과를 acc_test_result.txt에 저장했습니다.")

asyncio.run(test())
