import asyncio
import time
import json
from fast_l2m_scanner import run_fast_scanner as scan_w
from fast_armor_scanner import run_fast_armor_scanner as scan_a

async def main():
    start_time = time.time()
    
    r1 = await scan_w(1, 10.0, 7)
    r2 = await scan_w(2, 10.0, 7)
    r3 = await scan_a(1, 10.0, 5)
    r4 = await scan_a(2, 10.0, 5)
    r5 = await scan_w(1, 10.0, 8)
    r6 = await scan_w(2, 10.0, 8)
    r7 = await scan_a(1, 10.0, 6)
    r8 = await scan_a(2, 10.0, 6)
    
    total_time = time.time() - start_time
    
    results = {
        "time": total_time,
        "r1": r1, "r2": r2, "r3": r3, "r4": r4,
        "r5": r5, "r6": r6, "r7": r7, "r8": r8
    }
    
    with open("final_report.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    asyncio.run(main())
