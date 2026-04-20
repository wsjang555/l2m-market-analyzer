import requests
import json

api_key = "eyJraWQiOiI0OGEzNzliNS1mNGIxLTQ2Y2ItYTk4Zi0xOWNmM2VjOTEyYTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOiIwM0YxN0Y3NS1BM0E4LUUwMTEtQjlBOS1FNjFGMTM1RTk5MkYifQ.LN6qBKk0AgK-LY9j1apQXvq9BjeZMgUFHNMWz1eOizSlzn2HG2bl2r3reL6XVIEyPqTUknE4iy9UQvy3xWjKe7MENEvAJKjm3t7gPCQ-yjiq9p9kvI1GL-8vW57OTVOqPLHehogY4eZ7MeFex_UpaE3X1RHQchHSpyg1ZDe7oNqwsd6hg2CZ9brU0fhJHzwcVrqgc4aUZyEn7XotdN8fgN5I1Wq0VsZTW7ThL5N0262g2GtakFSmsm8fOdhEo6FM8r26aZ9uxr_t1dBQbgpPfOwf3rzGJttmydlI143u37Va6w1XbZLN96f-gaPE6s0PGeF_-U3E-RSAxcr1Kcd7OQ"
headers = {"Authorization": f"Bearer {api_key}"}

search_url = "https://dev-api.plaync.com/l2m/v1.0/market/items/search"

# Generous list of keywords to catch green weapons.
# Since the API search returns up to 'size' items (max 50-100), we use broad weapon types or specific popular green weapon keywords.
keywords = [
    "카르미안", "다마스커스", "은날의", "카타나", "플람베르그", "혁명의",
    "미스릴", "다크 스크리머", "악마의", "페어리", "척살의",
    "크리스", "카트리스", "샐러맨더", "환영의", "무명",
    "오키쉬", "드워븐", "스콜피온", "크림슨",
    "컴포지트", "엘븐", "강화 롱 보우", "호플론", "악몽의",
    "아이스", "아이젠", "사제의", "성자의", "크리스탈", "현자의", "데몬의",
    "은빛", "이클립스", "블러드", "츠바이핸더", "도깨비참", "타이탄",
    "검", "활", "단검", "지팡이", "오브", "창", "이도류", "석궁", "대검", "체인소드"
]

unique_items = {} # id -> name

for w in keywords:
    query = {"search_keyword": w, "size": 100}
    res = requests.get(search_url, headers=headers, params=query)
    if res.status_code == 200:
        contents = res.json().get('contents', [])
        for item in contents:
            # Check if green (grade 2)
            if item.get('grade') == 2:
                i_id = item.get('item_id')
                name = item.get('item_name')
                
                # Weak heuristic to skip obvious armor:
                if any(x in name for x in ["망토", "셔츠", "부츠", "장갑", "투구", "각반", "반지", "목걸이", "귀걸이", "벨트", "시길", "방패", "가더", "흉갑", "아머", "건틀릿", "헬멧", "티셔츠", "브레스트"]):
                    continue
                
                if name not in unique_items.values():
                    unique_items[i_id] = name

print(f"Found {len(unique_items)} candidate green items. Checking prices...")

results = []
count = 0
for i_id, name in unique_items.items():
    p0_url = f"https://dev-api.plaync.com/l2m/v1.0/market/items/{i_id}/price"
    p0_res = requests.get(p0_url, headers=headers, params={"server_id": 1211, "enchant_level": 0})
    count += 1
    if p0_res.status_code == 200:
        p0_now = p0_res.json().get('now', {}).get('unit_price')
        if p0_now == 10.0:
            # Qualifies! Check +7 price
            p7_res = requests.get(p0_url, headers=headers, params={"server_id": 1211, "enchant_level": 7})
            if p7_res.status_code == 200:
                p7_now = p7_res.json().get('now', {}).get('unit_price')
                if p7_now:
                    results.append({"name": name, "p7": p7_now})

# Sort results by p7 price descending
results.sort(key=lambda x: x['p7'], reverse=True)

print(f"\nTop Green Weapons (0강=10, 7강 가격순):")
for r in results[:3]:
    print(f"{r['name']} (+7): {r['p7']} 다이아")
