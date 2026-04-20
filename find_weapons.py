import requests
import json

api_key = "eyJraWQiOiI0OGEzNzliNS1mNGIxLTQ2Y2ItYTk4Zi0xOWNmM2VjOTEyYTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOiIwM0YxN0Y3NS1BM0E4LUUwMTEtQjlBOS1FNjFGMTM1RTk5MkYifQ.LN6qBKk0AgK-LY9j1apQXvq9BjeZMgUFHNMWz1eOizSlzn2HG2bl2r3reL6XVIEyPqTUknE4iy9UQvy3xWjKe7MENEvAJKjm3t7gPCQ-yjiq9p9kvI1GL-8vW57OTVOqPLHehogY4eZ7MeFex_UpaE3X1RHQchHSpyg1ZDe7oNqwsd6hg2CZ9brU0fhJHzwcVrqgc4aUZyEn7XotdN8fgN5I1Wq0VsZTW7ThL5N0262g2GtakFSmsm8fOdhEo6FM8r26aZ9uxr_t1dBQbgpPfOwf3rzGJttmydlI143u37Va6w1XbZLN96f-gaPE6s0PGeF_-U3E-RSAxcr1Kcd7OQ"
headers = {"Authorization": f"Bearer {api_key}"}

search_url = "https://dev-api.plaync.com/l2m/v1.0/market/items/search"

# Let's see if we can search for all items by passing empty keyword, or find out what metadata is available
keywords = ["롱 소드", "브로드 소드", "바스타드 소드", "더크", "스틸레토", "엘븐 보우",
            "사냥꾼의 활", "참나무 지팡이", "미스릴 지팡이", "구울의 지팡이",
            "파르티잔", "할버드", "롱 보우", "숏 보우", "글라디우스", "단검", "창",
            "이도류", "견습용 이도류", "나무 오브", "견습용 오브", "견습용 지팡이",
            "견습용 활", "견습용 단검", "견습용 롱 소드", "견습용 석궁", "석궁"]

unique_items = {} # id -> name

for w in keywords:
    query = {"search_keyword": w}
    res = requests.get(search_url, headers=headers, params=query)
    if res.status_code == 200:
        contents = res.json().get('contents', [])
        for item in contents:
            i_id = item.get('item_id')
            name = item.get('item_name')
            # Assuming these matched items are indeed white weapons if they are exactly the keyword
            if w == name and name not in unique_items.values():
                unique_items[i_id] = name

results = []
print(f"Found {len(unique_items)} unique normal weapons. Checking prices...")

for i_id, name in unique_items.items():
    p0_url = f"https://dev-api.plaync.com/l2m/v1.0/market/items/{i_id}/price"
    p0_res = requests.get(p0_url, headers=headers, params={"server_id": 1211, "enchant_level": 0})
    if p0_res.status_code == 200:
        p0_now = p0_res.json().get('now', {}).get('unit_price')
        if p0_now == 10.0:
            p7_res = requests.get(p0_url, headers=headers, params={"server_id": 1211, "enchant_level": 7})
            if p7_res.status_code == 200:
                p7_now = p7_res.json().get('now', {}).get('unit_price')
                if p7_now:
                    results.append({"name": name, "p7": p7_now})

results.sort(key=lambda x: x['p7'], reverse=True)

print(f"Top 3 White Weapons (0강=10, 7강 가격순):")
for r in results[:3]:
    print(f"{r['name']} (+7): {r['p7']} 다이아")


