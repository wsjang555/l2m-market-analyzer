/* app.js v2 */
document.addEventListener('DOMContentLoaded', () => {
    const btnScan   = document.getElementById('btn-scan');
    const btnReset  = document.getElementById('btn-refresh-cache');
    const loader    = document.getElementById('loader');
    const scanTimeEl= document.getElementById('scan-time');

    const dashBlue  = document.getElementById('dash-blue');
    const dashGreen = document.getElementById('dash-green');
    const dashWhite = document.getElementById('dash-white');

    const RANK_MEDALS = ['🥇','🥈','🥉','4위','5위'];

    // ── 탭 전환 ──────────────────────────────────────────────
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const g = tab.dataset.grade;
            [dashBlue, dashGreen, dashWhite].forEach(d => d.classList.add('hidden'));
            ({ blue: dashBlue, green: dashGreen, white: dashWhite })[g].classList.remove('hidden');
        });
    });

    // ── 섹션 카드 렌더 ────────────────────────────────────────
    const renderSection = (title, items, enchantLevel, theme, delayIdx) => {
        const sec = document.createElement('div');
        sec.className = `scan-section ${theme}-theme`;
        sec.style.animationDelay = `${delayIdx * 0.1}s`;

        let rowsHtml = '';
        if (!items || items.length === 0) {
            rowsHtml = `<div class="no-data">매물 없음 (0강 또는 +${enchantLevel}강 거래소 미등록)</div>`;
        } else {
            items.forEach((item, idx) => {
                const p0   = item.p0   !== undefined ? item.p0   : '-';
                const pX   = item[`p${enchantLevel}`] !== undefined ? item[`p${enchantLevel}`] : '-';
                const diff = item.diff !== undefined ? item.diff : '-';
                rowsHtml += `
                <div class="item-row ${idx===0?'item-top':''}">
                    <div class="item-rank">${RANK_MEDALS[idx]||`${idx+1}위`}</div>
                    <div class="item-info">
                        <div class="item-name">${item.name}</div>
                        <div class="item-prices">
                            <span class="price-tag p0-tag">0강 <strong>${p0}</strong> 💎</span>
                            <span class="arrow">→</span>
                            <span class="price-tag pX-tag">+${enchantLevel}강 <strong>${pX}</strong> 💎</span>
                        </div>
                    </div>
                    <div class="item-diff">
                        <span class="diff-label">차익</span>
                        <span class="diff-value">+${diff} 💎</span>
                    </div>
                </div>`;
            });
        }

        sec.innerHTML = `
            <div class="section-header">
                <span class="section-dot"></span>
                <span class="section-title">${title}</span>
            </div>
            <div class="section-body">${rowsHtml}</div>`;
        return sec;
    };

    // ── 대시보드 채우기 ───────────────────────────────────────
    const fillDashboard = (data) => {
        const wLv = data.weapon_level ?? 7;
        const aLv = data.armor_level  ?? 5;

        // 파란색
        dashBlue.innerHTML = '';
        const blueRow = document.createElement('div');
        blueRow.className = 'section-row';
        blueRow.appendChild(renderSection(`파란색 무기 +${wLv}강 차익 Top5`,  data.blue_weapons,  wLv, 'blue',  0));
        blueRow.appendChild(renderSection(`파란색 방어구 +${aLv}강 차익 Top5`, data.blue_armors,   aLv, 'blue',  1));
        dashBlue.appendChild(blueRow);

        // 초록색
        dashGreen.innerHTML = '';
        const greenRow = document.createElement('div');
        greenRow.className = 'section-row';
        greenRow.appendChild(renderSection(`초록색 무기 +${wLv}강 차익 Top5`,  data.green_weapons, wLv, 'green', 0));
        greenRow.appendChild(renderSection(`초록색 방어구 +${aLv}강 차익 Top5`, data.green_armors,  aLv, 'green', 1));
        dashGreen.appendChild(greenRow);

        // 하얀색
        dashWhite.innerHTML = '';
        const whiteRow = document.createElement('div');
        whiteRow.className = 'section-row';
        whiteRow.appendChild(renderSection(`하얀색 무기 +${wLv}강 차익 Top5`,  data.white_weapons, wLv, 'white', 0));
        whiteRow.appendChild(renderSection(`하얀색 방어구 +${aLv}강 차익 Top5`, data.white_armors,  aLv, 'white', 1));
        dashWhite.appendChild(whiteRow);
    };

    // ── 스캔 실행 ─────────────────────────────────────────────
    const performScan = async () => {
        btnScan.disabled  = true;
        btnScan.innerText = '스캔 중...';
        [dashBlue, dashGreen, dashWhite].forEach(d => d.innerHTML = '');
        loader.classList.remove('hidden');
        scanTimeEl.innerText = '스캔 진행 중...';

        try {
            const res  = await fetch('/api/scan');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            loader.classList.add('hidden');
            fillDashboard(data);
            const now = new Date();
            scanTimeEl.innerText = `최근 스캔: ${now.toLocaleTimeString('ko-KR')} (소요시간: ${data.time}초)`;
        } catch (err) {
            loader.classList.add('hidden');
            alert('스캔 중 오류가 발생했습니다. 서버 연결 확인하세요.');
            console.error(err);
        } finally {
            btnScan.disabled  = false;
            btnScan.innerText = '스캔 시작 🚀';
        }
    };

    // ── 캐시 초기화 ───────────────────────────────────────────
    const resetCache = async () => {
        if (!confirm('DB 캐시를 모두 삭제하고 재스캔합니까?\n(전 등급 DB 재구축 — 수 분 소요)')) return;
        btnReset.disabled  = true;
        btnReset.innerText = '초기화 중...';
        try {
            const res = await fetch('/api/reset_cache', { method: 'POST' });
            await res.json();
            alert('삭제 완료! [스캔 시작]을 눌러 DB를 재구축하세요.');
        } catch {
            alert('초기화 실패');
        } finally {
            btnReset.disabled  = false;
            btnReset.innerText = 'DB 강제초기화';
        }
    };

    btnScan.addEventListener('click', performScan);
    btnReset.addEventListener('click', resetCache);

    // 최초 자동 스캔
    performScan();
});
