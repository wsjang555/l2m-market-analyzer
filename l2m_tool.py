import requests
import sys
import json

if len(sys.argv) < 2:
    print("Usage: python l2m_tool.py <search_keyword>")
    sys.exit(1)

keyword = sys.argv[1]

api_key = "eyJraWQiOiI0OGEzNzliNS1mNGIxLTQ2Y2ItYTk4Zi0xOWNmM2VjOTEyYTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOiIwM0YxN0Y3NS1BM0E4LUUwMTEtQjlBOS1FNjFGMTM1RTk5MkYifQ.LN6qBKk0AgK-LY9j1apQXvq9BjeZMgUFHNMWz1eOizSlzn2HG2bl2r3reL6XVIEyPqTUknE4iy9UQvy3xWjKe7MENEvAJKjm3t7gPCQ-yjiq9p9kvI1GL-8vW57OTVOqPLHehogY4eZ7MeFex_UpaE3X1RHQchHSpyg1ZDe7oNqwsd6hg2CZ9brU0fhJHzwcVrqgc4aUZyEn7XotdN8fgN5I1Wq0VsZTW7ThL5N0262g2GtakFSmsm8fOdhEo6FM8r26aZ9uxr_t1dBQbgpPfOwf3rzGJttmydlI143u37Va6w1XbZLN96f-gaPE6s0PGeF_-U3E-RSAxcr1Kcd7OQ"

headers = {
    "Authorization": f"Bearer {api_key}"
}

# 1211 is 데스나이트 world id. If we use POST or GET? We saw GET worked for servers, let's try POST or GET.
# The API spec says the market search endpoint is: GET /l2m/v1.0/market/items/search
# 데스나이트01~10: 211 ~ 220
search_url = "https://dev-api.plaync.com/l2m/v1.0/market/items/search"
found = False

try:
    print(f"== 데스나이트 서버 그룹 [{keyword}] 매물 검색 ==")
    for server_id in range(211, 221):
        query = {"search_keyword": keyword, "from_enchant_level": 0, "to_enchant_level": 9, "server_id": server_id}
        search_res = requests.get(search_url, headers=headers, params=query)
        data = search_res.json()
        if search_res.status_code == 200:
            contents = data.get('contents', [])
            for item in contents[:5]:  # show top 5 per server
                name = item.get('item_name')
                enchant = item.get('enchant_level', 0)
                price = item.get('unit_price', item.get('price', 0))
                if price == 0: continue
                found = True
                server = item.get('server_name', f'데스나이트{server_id-210:02d}')
                enchant_str = f"+{enchant}" if enchant > 0 else ""
                print(f"서버: {server} | 아이템: {enchant_str} {name} | 최저가(다이아): {price}")
        else:
            print(f"API 에러(Server {server_id}):", data)

    if not found:
        print(f"[{keyword}] 매물이 현재 데스나이트 서버 그룹의 거래소에 없습니다.")
except Exception as e:
    print("Error:", e)
