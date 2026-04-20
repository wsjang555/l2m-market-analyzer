import asyncio
from fast_l2m_scanner import run_fast_scanner as scan_w
from fast_armor_scanner import run_fast_armor_scanner as scan_a

async def main():
    print("\n\n========== 1. 하얀색(일반) 무기, 0강 10다이아, 7강 조사 ==========")
    await scan_w(1, 10.0, 7)
    print("\n\n========== 2. 녹색(고급) 무기, 0강 10다이아, 7강 조사 ==========")
    await scan_w(2, 10.0, 7)

    print("\n\n========== 3. 하얀색(일반) 방어구, 0강 10다이아, 5강 조사 ==========")
    await scan_a(1, 10.0, 5)
    print("\n\n========== 4. 녹색(고급) 방어구, 0강 10다이아, 5강 조사 ==========")
    await scan_a(2, 10.0, 5)

    print("\n\n========== 5. 하얀색(일반) 무기, 0강 10다이아, 8강 조사 ==========")
    await scan_w(1, 10.0, 8)
    print("\n\n========== 6. 녹색(고급) 무기, 0강 10다이아, 8강 조사 ==========")
    await scan_w(2, 10.0, 8)

    print("\n\n========== 7. 하얀색(일반) 방어구, 0강 10다이아, 6강 조사 ==========")
    await scan_a(1, 10.0, 6)
    print("\n\n========== 8. 녹색(고급) 방어구, 0강 10다이아, 6강 조사 ==========")
    await scan_a(2, 10.0, 6)

if __name__ == '__main__':
    asyncio.run(main())
