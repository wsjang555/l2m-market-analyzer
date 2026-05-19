/* app.js v3 — 요청 목록 전용 */
document.addEventListener('DOMContentLoaded', () => {
    const btnScan   = document.getElementById('btn-scan');
    const btnReset  = document.getElementById('btn-refresh-cache');
    const loader    = document.getElementById('loader');
    const scanTimeEl= document.getElementById('scan-time');

    const dashBlue  = document.getElementById('dash-blue');
    const dashGreen = document.getElementById('dash-green');
    const dashWhite = document.getElementById('dash-white');

    const RANK_MEDALS = ['🥇','🥈','🥉'];

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

    // ── 차익 섹션 렌더 ────────────────────────────────────────
    const renderSection = (title, items, enchantLevel, theme, delayIdx) => {
        const sec = document.createElement('div');
        sec.className = `scan-section ${theme}-theme`;
        sec.style.animationDelay = `${delayIdx * 0.08}s`;

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

    // ── 한 등급 탭의 섹션 그룹 빌드 ─────────────────────────────
    // weaponSections: [{key, level, label}, ...]
    // armorSections:  [{key, level, label}, ...]
    const buildTab = (container, theme, weaponSections, armorSections, data) => {
        container.innerHTML = '';
        let delayIdx = 0;

        // 무기 + 방어구를 짝지어 section-row로 배치
        const maxLen = Math.max(weaponSections.length, armorSections.length);
        for (let i = 0; i < maxLen; i++) {
            const row = document.createElement('div');
            row.className = 'section-row';

            if (i < weaponSections.length) {
                const ws = weaponSections[i];
                row.appendChild(renderSection(ws.label, data[ws.key], ws.level, theme, delayIdx++));
            }
            if (i < armorSections.length) {
                const as_ = armorSections[i];
                row.appendChild(renderSection(as_.label, data[as_.key], as_.level, theme, delayIdx++));
            }

            container.appendChild(row);
        }
    };

    // ── 대시보드 채우기 ───────────────────────────────────────
    const fillDashboard = (data) => {

        // ── 희귀(파란색): 무기+7, 방어구+5 ──────────────────────
        buildTab(
            dashBlue, 'blue',
            [{ key: 'blue_weapons_7', level: 7, label: '🔵 희귀 무기 +7강 차익 Top3' }],
            [{ key: 'blue_armors_5',  level: 5, label: '🔵 희귀 방어구 +5강 차익 Top3' }],
            data
        );

        // ── 고급(초록색): 무기+7/8/9, 방어구+5/6/7 ───────────────
        buildTab(
            dashGreen, 'green',
            [
                { key: 'green_weapons_7', level: 7, label: '🟢 고급 무기 +7강 차익 Top3' },
                { key: 'green_weapons_8', level: 8, label: '🟢 고급 무기 +8강 차익 Top3' },
                { key: 'green_weapons_9', level: 9, label: '🟢 고급 무기 +9강 차익 Top3' },
            ],
            [
                { key: 'green_armors_5', level: 5, label: '🟢 고급 방어구 +5강 차익 Top3' },
                { key: 'green_armors_6', level: 6, label: '🟢 고급 방어구 +6강 차익 Top3' },
                { key: 'green_armors_7', level: 7, label: '🟢 고급 방어구 +7강 차익 Top3' },
            ],
            data
        );

        // ── 일반(하얀색): 무기+7/8/9, 방어구+5/6/7 ───────────────
        buildTab(
            dashWhite, 'white',
            [
                { key: 'white_weapons_7', level: 7, label: '⚪ 일반 무기 +7강 차익 Top3' },
                { key: 'white_weapons_8', level: 8, label: '⚪ 일반 무기 +8강 차익 Top3' },
                { key: 'white_weapons_9', level: 9, label: '⚪ 일반 무기 +9강 차익 Top3' },
            ],
            [
                { key: 'white_armors_5', level: 5, label: '⚪ 일반 방어구 +5강 차익 Top3' },
                { key: 'white_armors_6', level: 6, label: '⚪ 일반 방어구 +6강 차익 Top3' },
                { key: 'white_armors_7', level: 7, label: '⚪ 일반 방어구 +7강 차익 Top3' },
            ],
            data
        );
    };

    // ── 스캔 실행 ─────────────────────────────────────────────
    let elapsedTimer = null;

    const startElapsedTimer = () => {
        const startAt = Date.now();
        scanTimeEl.innerText = '스캔 진행 중... 0초';
        elapsedTimer = setInterval(() => {
            const sec = Math.floor((Date.now() - startAt) / 1000);
            scanTimeEl.innerText = `스캔 진행 중... ${sec}초 (최대 120초)`;
        }, 1000);
    };

    const stopElapsedTimer = () => {
        if (elapsedTimer) { clearInterval(elapsedTimer); elapsedTimer = null; }
    };

    const performScan = async () => {
        btnScan.disabled  = true;
        btnScan.innerText = '스캔 중...';
        [dashBlue, dashGreen, dashWhite].forEach(d => d.innerHTML = '');
        loader.classList.remove('hidden');
        startElapsedTimer();

        const controller = new AbortController();
        const timeoutId  = setTimeout(() => controller.abort(), 120_000);

        try {
            const res  = await fetch('/api/scan', { signal: controller.signal });
            clearTimeout(timeoutId);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            stopElapsedTimer();
            loader.classList.add('hidden');
            fillDashboard(data);
            const now = new Date();
            scanTimeEl.innerText = `최근 스캔: ${now.toLocaleTimeString('ko-KR')} (소요시간: ${data.time}초)`;
        } catch (err) {
            clearTimeout(timeoutId);
            stopElapsedTimer();
            loader.classList.add('hidden');
            if (err.name === 'AbortError') {
                alert('⏱ 스캔 시간이 너무 오래 걸립니다.\n서버가 잠들었을 수 있습니다. 30초 후 다시 시도해 주세요.');
            } else {
                alert(`스캔 오류: ${err.message}\n\n잠시 후 다시 시도해 주세요.`);
            }
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
