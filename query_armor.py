import requests
import json

api_key = "eyJraWQiOiI0OGEzNzliNS1mNGIxLTQ2Y2ItYTk4Zi0xOWNmM2VjOTEyYTYiLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOiIwM0YxN0Y3NS1BM0E4LUUwMTEtQjlBOS1FNjFGMTM1RTk5MkYifQ.LN6qBKk0AgK-LY9j1apQXvq9BjeZMgUFHNMWz1eOizSlzn2HG2bl2r3reL6XVIEyPqTUknE4iy9UQvy3xWjKe7MENEvAJKjm3t7gPCQ-yjiq9p9kvI1GL-8vW57OTVOqPLHehogY4eZ7MeFex_UpaE3X1RHQchHSpyg1ZDe7oNqwsd6hg2CZ9brU0fhJHzwcVrqgc4aUZyEn7XotdN8fgN5I1Wq0VsZTW7ThL5N0262g2GtakFSmsm8fOdhEo6FM8r26aZ9uxr_t1dBQbgpPfOwf3rzGJttmydlI143u37Va6w1XbZLN96f-gaPE6s0PGeF_-U3E-RSAxcr1Kcd7OQ"
headers = {"Authorization": f"Bearer {api_key}"}

i_id = 200140006
price_url = f"https://dev-api.plaync.com/l2m/v1.0/market/items/{i_id}/price"

print("Checking server_id=1211 (World Exchange)...")
for enc in [4, 5, 6]:
    q2 = {"server_id": 1211, "enchant_level": enc}
    res2 = requests.get(price_url, headers=headers, params=q2)
    if res2.status_code == 200:
        data = res2.json()
        now_price = data.get('now', {}).get('unit_price')
        if now_price:
            print(f"+{enc} price: {now_price}")
        else:
            print(f"+{enc} no item")
    else:
        print(f"Error {enc}:", res2.status_code)
print("Done.")
    

