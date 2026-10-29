// Вкладка "История группы" (exams.html -> #tabHistory)
// Данные те же, что у вкладки "Сравнение периодов": getComparisonData() из exams_compare.js
// (подключён раньше). Заглушка и переход на настоящие данные - в exams_compare.js, здесь ничего менять не нужно.
// Вкладками управляет exams_analytics.js (событие 'main-tab').

const HIST_PASS_PERCENT = 65   // порог сдачи КПИ, как KPI_PASS_PERCENT в teacher/utils.py

let histData = null        // ответ fetch_exams_comparison
let histLoaded = false
let histActive = false
let histRequestId = 0

const $h = id => document.getElementById(id)

const histEsc = v => String(v ?? '').replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[ch]))

const histPercent = (a, b) => b ? Math.round(a / b * 100) : null

// ---------- события ----------
window.addEventListener('main-tab', e => {
    histActive = e.detail === 'history'
    if (histActive) loadHistory()
})

// вызывается из exams.js после перезагрузки данных (смена группы, новый результат)
window.refreshHistory = () => {
    histLoaded = false
    if (histActive) loadHistory()
}

$h('kindSelect')?.addEventListener('change', () => {
    if (histActive && histData) renderHistory()
})

// кнопки в списке (делегирование: список пересоздаётся)
$h('histList')?.addEventListener('click', e => {
    const open = e.target.closest('[data-hist-open]')
    if (open) return window.openAnalyticsFor?.(Number(open.dataset.histOpen))
    const cmp = e.target.closest('[data-hist-compare]')
    if (cmp) return window.openCompareFor?.(Number(cmp.dataset.histCompare))
})

// ---------- загрузка ----------
function loadHistory() {
    if (histLoaded && histData) return renderHistory()
    const id = ++histRequestId
    getComparisonData()
        .then(data => {
            if (id !== histRequestId) return   // ответ для уже сменённой группы
            histData = data
            histLoaded = true
            renderHistory()
        })
        .catch(err => console.error(err))
}

// ---------- расчёт по каждому КПИ ----------
function histKindTests() {
    const text = $h('kindSelect')?.value || ''
    const kind = text.startsWith('ОФП +') ? 'all' : text === 'ОФП' ? 'general' : text === 'СФП' ? 'special' : 'all'
    return histData.tests.filter(t => kind === 'all' || (kind === 'general' ? t.type === 'general' : t.type !== 'general'))
}

const histMeasured = v => v && v.score !== null && v.score !== undefined && ['passed', 'failed'].includes(v.result)

function histSummary(period, tests) {
    const id = String(period.id)
    // в программу КПИ входят испытания, по которым в этом КПИ есть хоть одна запись
    const program = tests.filter(t => t.rows.some(r => r.values[id]))
    const n = tests[0]?.rows.length ?? 0

    let filled = 0, measured = 0, passedM = 0, passedKpi = 0
    for (let i = 0; i < n; i++) {
        let passed = 0, required = 0
        program.forEach(t => {
            const v = t.rows[i].values[id]
            if (v && v.result !== 'empty') filled++
            if (histMeasured(v)) {
                measured++
                if (v.result === 'passed') passedM++
            }
            if (v?.result === 'passed') passed++
            if (v?.result !== 'exempted') required++       // освобождённые испытания не считаются
        })
        // правило КПИ (как в шапке и аналитике): >= 65% сданных = сдал КПИ
        if (required && Math.round(passed / required * 100) >= HIST_PASS_PERCENT) passedKpi++
    }
    return {n, total: n * program.length, filled, measured, passedM, passedKpi}
}

// ---------- отрисовка ----------
function renderHistory() {
    if (!histData.periods.length) {
        $h('histList').innerHTML = '<p class="text-center text-muted py-4 mb-0">Для этой группы пока нет КПИ.</p>'
        $h('histChart').innerHTML = ''
        $h('histPeriods').innerHTML = ''
        return
    }
    const tests = histKindTests()
    const summaries = histData.periods.map(p => histSummary(p, tests))

    $h('histChart').innerHTML = histChart(summaries)
    $h('histPeriods').innerHTML = histData.periods.map((p, i) => `
        <div><strong>${histEsc(p.name)}</strong>
        <span>${summaries[i].measured ? `${summaries[i].passedM} из ${summaries[i].measured} сданы` : 'Нет замеров'}</span></div>`).join('')

    // новые КПИ сверху
    $h('histList').innerHTML = histData.periods.map((p, i) => ({p, i, s: summaries[i]})).reverse().map(({p, i, s}) => `
        <article class="hist-item">
            <div class="hist-main">
                <div>
                    <h3>${histEsc(p.name)}</h3>
                    <p class="an-sub">${histEsc(p.date_start)} — ${histEsc(p.date_end)}</p>
                </div>
                <p class="hist-score"><b>${s.passedKpi} из ${s.n}</b> сдали КПИ</p>
                <button type="button" class="btn btn-outline-secondary btn-sm" data-hist-open="${p.id}">Открыть →</button>
            </div>
            <details class="hist-detail">
                <summary>Подробнее о периоде</summary>
                <p>Заполнено результатов: ${s.filled} из ${s.total}. Сданы ${s.passedM} из ${s.measured} попыток с замером.</p>
                ${i ? `<button type="button" class="btn btn-outline-secondary btn-sm" data-hist-compare="${p.id}">Сравнить с предыдущим периодом</button>` : ''}
            </details>
        </article>`).join('')
}

// Линейный график: доля сданных попыток среди замеров по каждому КПИ. Период без замеров - разрыв линии.
function histChart(summaries) {
    const left = 65, right = 545, top = 35, bottom = 205
    const step = summaries.length > 1 ? (right - left) / (summaries.length - 1) : 0
    const data = summaries.map((s, i) => ({
        x: summaries.length > 1 ? left + i * step : (left + right) / 2,
        value: histPercent(s.passedM, s.measured),
        name: histData.periods[i].name,
    })).map(d => ({...d, y: d.value === null ? null : bottom - d.value / 100 * (bottom - top)}))

    const segments = []
    let segment = []
    data.forEach(d => {
        if (d.y === null) { if (segment.length) segments.push(segment); segment = [] }
        else segment.push(`${d.x},${d.y}`)
    })
    if (segment.length) segments.push(segment)

    const grid = [0, 25, 50, 75, 100].map(v => {
        const y = bottom - v / 100 * (bottom - top)
        return `<line x1="55" x2="555" y1="${y}" y2="${y}" stroke="#e5eaf1"/>
                <text x="43" y="${y + 4}" fill="#647185" text-anchor="end" font-size="12">${v}%</text>`
    }).join('')

    const points = data.map(d => `
        ${d.y === null ? '' : `<circle cx="${d.x}" cy="${d.y}" r="6" fill="#345fd4" stroke="white" stroke-width="3"/>
        <text x="${d.x}" y="${d.y - 15}" text-anchor="middle" fill="#345fd4" font-size="16" font-weight="600">${d.value}%</text>`}
        <text x="${d.x}" y="240" text-anchor="middle" fill="#526179" font-size="13">${histEsc(d.name.length > 16 ? d.name.slice(0, 15) + '…' : d.name)}</text>`).join('')

    const desc = data.map(d => `${d.name}: ${d.value === null ? 'нет замеров' : d.value + '%'}`).join('. ')
    return `<svg class="hist-svg" viewBox="0 0 610 260" role="img" aria-label="Прогресс группы по КПИ">
        <title>Прогресс группы</title><desc>${histEsc(desc)}. Пропуски и освобождения не учитываются.</desc>
        ${grid}
        ${segments.map(pts => `<polyline points="${pts.join(' ')}" fill="none" stroke="#345fd4" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>`).join('')}
        ${points}
    </svg>`
}
