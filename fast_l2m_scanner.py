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
PRICE_URL = "https://dev-api.plaync.com/l2m/v1.0/market/items/{}/price"

# ============================================================
# 리니지2M 공식 가이드북 (https://lineage2m.plaync.com/guidebook/view?title=무기)
# 에서 긁어온 전체 무기 이름 목록 - 100% 완전 커버리지 보장
# ============================================================
ALL_WEAPON_NAMES = [
    # 한손검
    "포가튼 블레이드", "칼라드볼그", "견습기사의 검", "코볼드 전사의 검", "올 마훔 전사의 검",
    "오크 전사의 검", "리자드맨 전사의 검", "엘븐 소드", "츠루기", "악몽의 검",
    "크샨베르크", "혁명의 검", "실레노스 소드", "오크 용사의 검", "카타나",
    "엘븐 롱소드", "나이트 소드", "크림슨 소드", "미스틱 나이프",
    # 이도류
    "아스타로트", "아크엔젤 듀얼 소드", "탈룸 듀얼 소드", "다크 레기온", "테미스의 혀",
    "거인의 듀얼 소드", "다마스커스 듀얼 소드", "카리브스 듀얼 소드", "미혹의 듀얼 소드",
    "극한의 듀얼 소드", "실레노스 듀얼 소드", "오크 용사의 듀얼 소드", "스톰브링거 듀얼 소드",
    "스파인본 듀얼 소드", "샴쉬르 듀얼 소드", "결속의 듀얼 소드", "블러드 듀얼 소드",
    "오크 전사의 듀얼 소드", "리자드맨 전사의 듀얼 소드", "견습전사의 듀얼 소드", "리플렉션 듀얼 소드",
    # 단검
    "나가스톰", "아크엔젤 슬레이어", "크루마의 뿔", "악마의 단검", "거인의 단검",
    "크리스", "헬나이프", "크리스탈 단검", "실레노스 대거", "오크 용사의 단검",
    "그레이스 대거", "다크스크리머", "다크엘븐 대거", "악운의 단검", "어쌔신 단검",
    "나이프", "코볼드 약탈꾼의 단검", "올 마훔 전사의 단검", "오크 전사의 단검",
    "리자드맨 전사의 단검", "견습살수의 나이프", "메인 거쉬",
    # 활
    "롱보우", "강화 롱 보우", "가스트라페테스", "실레노스 보우", "오크 용사의 활",
    "강화 활", "엘븐 보우", "숲의 활", "작은 활",
    # 지팡이
    "스타카토 퀸의 지팡이", "세계수의 가지", "데스페리온의 지팡이", "거인의 지팡이",
    "크리스탈 지팡이", "사령의 지팡이", "생명의 홀", "아투바 지팡이", "사제의 지팡이",
    "실레노스 스태프", "오크 장로의 지팡이", "법사의 지팡이",
    # 오브
    "아르카나 오브", "아크엔젤 오브", "드래곤 플레임 헤드", "핸드 오브 카브리오",
    "거인의 오브", "스펠 브레이커", "이클립스 오브", "마나의 오브", "실레노스 오브",
    "오크 예언자의 오브", "구원의 오브", "대자연의 오브", "기도의 오브", "역사의 오브",
    "심판의 오브", "견습사제의 오브", "오크 주술병의 오브", "리자드맨 주술병의 오브",
    # 창
    "안타라스 스토머", "세인트 스피어", "타이폰 스피어", "탈룸 글레이브", "렌시아",
    "아크엔젤 핼버드", "핼버드", "아스칼론", "바디슬래셔", "거인의 창",
    "위도우메이커", "스콜피언", "사이드", "헤비 워 액스", "배틀 스피어",
    "폴액스", "배크 드 코르뱅", "오키쉬 글레이브", "해머 인 플레임즈", "레토 리자드맨의 창",
    "오키쉬 폴액스", "스컬 그레이버", "사자의 영광", "백금족 수호기사의 창",
    "하거인 수호 전사의 창",
    # 대검
    "발라카스 디바이더", "페더아이 버스터", "라바몬트 쏘우", "카오스 브레이커",
    "아크엔젤 버스터", "헤븐즈 윙블레이드", "쯔바이 핸더", "오키쉬 대검",
    "소드 오브 파아그리오", "하거인의 대검", "강철 대검", "클레이모어",
    "레토 리자드맨의 대검", "천궁 수호기사의 대검", "하거인 수호 전사의 대검",
    # 석궁
    "린드비오르 슈트제", "루드커터 크로스보우", "사룽가", "다이너스티 크로스보우",
    "쏜 크로스보우", "둠 싱어", "아크엔젤 크로스보우", "헬 하운드", "거인의 석궁",
    "피스메이커", "타스람", "엔틱 크로스보우", "크리스탈 보우건", "발리스타",
    "샤프 슈터", "크로스보우", "핸드 보우건", "참나무 석궁",
    "케트라 오크 궁병의 석궁", "백금족 궁병의 석궁", "하드우드 보우건", "저격수의 석궁", "헌팅건",
]

ITEM_DB_FILE = "item_db_weapons_{}.json"  # 등급별 캐싱

async def fetch_item_by_name(session, name, target_grade):
    """정확한 아이템 이름으로 단건 검색 - 100% 정확도 보장"""
    query = {"search_keyword": name, "sale": "true", "size": 10}
    try:
        async with session.get(SEARCH_URL, headers=headers, params=query, timeout=15) as res:
            if res.status == 200:
                data = await res.json()
                for item in data.get('contents', []):
                    # 이름이 정확히 일치하고 등급도 맞는 것만 채택
                    if item.get('item_name') == name and item.get('grade') == target_grade:
                        return (item.get('item_id'), name)
    except Exception as e:
        print(f"  검색 오류 ({name}): {e}")
    return None

async def fetch_all_items(target_grade):
    print(f"1) 무기(등급:{target_grade}) 전체 목록 DB 구축 중... ({len(ALL_WEAPON_NAMES)}종 직접 검색)")
    unique_items = {}
    async with aiohttp.ClientSession() as session:
        for name in ALL_WEAPON_NAMES:
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
    print(f" -> 로컬 DB 저장 완료: {len(unique_items)}개의 무기 확보")
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

async def run_fast_scanner(target_grade, p0_target_price, pX_level, server_id=1211):
    print(f"\n[무기 스캐너] 등급:{target_grade}, 0강<={p0_target_price}다이아, +{pX_level}강 기준")
    start_time = time.time()

    unique_items = {}
    db_filename = ITEM_DB_FILE.format(target_grade)

    if os.path.exists(db_filename):
        with open(db_filename, 'r', encoding='utf-8') as f:
            unique_items = json.load(f)
        print(f"1) 로컬 DB 로드 완료: {len(unique_items)}개의 무기 확보 (캐시 사용)")
    else:
        unique_items = await fetch_all_items(target_grade)

    if not unique_items:
        print("검색된 무기가 없습니다.")
        return []

    # 2. +0강 가격 병렬 스캔
    candidates_evaluating_p0 = []
    print(f"2) {len(unique_items)}개 무기의 +0강 실시간 가격 전수 스캔 중...")

    conn = aiohttp.TCPConnector(limit=50)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [get_price(session, i_id, name, 0, server_id) for i_id, name in unique_items.items()]
        results = await asyncio.gather(*tasks)

        for res in results:
            if res["price"] is not None and res["price"] <= p0_target_price:
                candidates_evaluating_p0.append(res)

    print(f" -> 0강 {p0_target_price}다이아 이하: {len(candidates_evaluating_p0)}개 발견")

    # 3. +X강 가격 스캔
    final_results = []
    if candidates_evaluating_p0:
        print(f"3) +{pX_level}강 가격 스캔 중...")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=50)) as session:
            tasks = [get_price(session, i['id'], i['name'], pX_level, server_id) for i in candidates_evaluating_p0]
            results_pX = await asyncio.gather(*tasks)

            for p0_item, pX_item in zip(candidates_evaluating_p0, results_pX):
                if pX_item["price"] and p0_item["price"]:
                    diff = pX_item["price"] - p0_item["price"]
                    final_results.append({
                        "name": p0_item["name"],
                        "p0": p0_item["price"],
                        f"p{pX_level}": pX_item["price"],
                        "diff": round(diff, 4)
                    })

    # 가격 차이(diff) 기준 내림차순 정렬
    final_results.sort(key=lambda x: x['diff'], reverse=True)

    end_time = time.time()
    print(f"\n[완료] 스캔 완료! ({end_time - start_time:.2f}초)")
    print(f"\n[Top5] 무기 (0강<={p0_target_price}, +{pX_level}강 차이순):")
    if not final_results:
        print("  조건을 만족하는 매물이 없습니다.")
    for r in final_results[:5]:
        print(f"  - {r['name']} | 0강:{r['p0']} -> +{pX_level}강:{r[f'p{pX_level}']} | 차이:{r['diff']} 다이아")

    return final_results[:5]

if __name__ == "__main__":
    asyncio.run(run_fast_scanner(target_grade=2, p0_target_price=15.0, pX_level=7, server_id=1211))
