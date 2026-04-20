import requests
import json

api_key = "eyJraWQiOiI0OGEzNzliNS1mNGIxLTQ2Y2ItYTk4Zi0xOWNmM2VjOTEyYTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOiIwM0YxN0Y3NS1BM0E4LUUwMTEtQjlBOS1FNjFGMTM1RTk5MkYifQ.LN6qBKk0AgK-LY9j1apQXvq9BjeZMgUFHNMWz1eOizSlzn2HG2bl2r3reL6XVIEyPqTUknE4iy9UQvy3xWjKe7MENEvAJKjm3t7gPCQ-yjiq9p9kvI1GL-8vW57OTVOqPLHehogY4eZ7MeFex_UpaE3X1RHQchHSpyg1ZDe7oNqwsd6hg2CZ9brU0fhJHzwcVrqgc4aUZyEn7XotdN8fgN5I1Wq0VsZTW7ThL5N0262g2GtakFSmsm8fOdhEo6FM8r26aZ9uxr_t1dBQbgpPfOwf3rzGJttmydlI143u37Va6w1XbZLN96f-gaPE6s0PGeF_-U3E-RSAxcr1Kcd7OQ"

headers = {
    "Authorization": f"Bearer {api_key}"
}

# 1. 서버 정보 조회 (서버 ID 확인용)
server_url = "https://dev-api.plaync.com/l2m/v1.0/market/servers"
res = requests.get(server_url, headers=headers)
server_data = res.json()
print("Servers response:", res.status_code)
death_knight_servers = []
for world in server_data:
    if "데스나이트" in world.get("world_name", ""):
        print(f"Found world: {world['world_name']} (ID: {world['world_id']})")
        for srv in world.get("servers", []):
            death_knight_servers.append((srv['server_name'], srv['server_id']))
            print(f" - {srv['server_name']}: {srv['server_id']}")

print("Death Knight servers:", death_knight_servers)

# test price query for item 503291001 (마검 비술서)
item_id = 503291001
server_id = 211 # 데스나이트01
price_url = f"https://dev-api.plaync.com/l2m/v1.0/market/items/{item_id}/price"
# let's try with server_id first
res_price = requests.get(price_url, headers=headers, params={"server_id": server_id})
print("Price response:", res_price.status_code, res_price.text[:1000])

# let's try with world_id
price_url2 = f"https://dev-api.plaync.com/l2m/v1.0/market/items/{item_id}/price"
res_price2 = requests.get(price_url2, headers=headers, params={"world_id": 1211})
print("Price world response:", res_price2.status_code, res_price2.text[:1000])

