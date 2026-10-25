let groupSelect = document.querySelector('.group_select')
let lastExamsData = null
let selectedAthleteId = null
let activeSideTab = 'dynamics'
let dynamicsCache = {}        // `${groupId}:${athleteId}` -> ответ сервера
let dynamicsTestId = null     // выбранное испытание на графике

document.addEventListener('DOMContentLoaded', () => {
    fetchData()
})

groupSelect.addEventListener('change', () => {
    hideAthleteSidebar()
    dynamicsPeriodId = null
    fetchData()

})

function fetchData() {
    let selectedGroup = groupSelect.value
    let queryParams = buildQueryParams({'group': selectedGroup})

    fetch(`/teacher/fetch_exams_data?${queryParams}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
    }).then(res =>
        res.json()
    ).then(data => {
        replaceData(data)
    })
        .catch(error => {
            console.error(error)
        });
}

function replaceData(data) {
    lastExamsData = data
    dynamicsRequestId += 1
    dynamicsCache = {}  // результаты могли измениться - история устарела
    document.querySelector('.total_number').textContent = data.students_count;

    ['passed', 'failed', 'absent'].forEach(status => {
        document.querySelector(`.${status}_number`).textContent = data[status];
        document.querySelector(`.${status}_percent`).textContent = `${data[`${status}_percent`]}%`;
    });
    renderTableHead(data.thead)
    renderTableBody(data.thead, data.table)
    window.refreshAnalytics?.()  // обновить вкладку аналитики, если она открыта
    document.querySelector('.avg_number').textContent = `${data.avg_percent}%`
    document.querySelector('.avg_percent').querySelector('div').style.width = `${data.avg_percent}%`

    if (selectedAthleteId && data.table[selectedAthleteId]) {
        renderAthleteSidebar(selectedAthleteId)

    } else {
        hideAthleteSidebar()

    }
}

function buildQueryParams(data) {
    //Функция принимает словарь и возвращает его в таком виде:'group=1&year=2026'
    let result = []

    for (let [key, value] of Object.entries(data)) {
        result.push(`${key}=${value}`)
    }
    return result.join('&')
}

function getCookie(name) {
    let value = null;
    if (document.cookie) {
        for (let c of document.cookie.split(';')) {
            c = c.trim();
            if (c.startsWith(name + '=')) {
                value = decodeURIComponent(c.substring(name.length + 1));
                break;
            }
        }
    }
    return value;
}

// Функция
function renderTableHead(testItems) {
    const thead = document.getElementById('examsTableHead')

    const generalItems = testItems.filter(item => item.assessment_type === 'general')
    const specialItems = testItems.filter(item => item.assessment_type === 'speсial')

    let groupRow = '<tr class="group-row"><th colspan="2"></th>'
    if (generalItems.length) {
        groupRow += `<th colspan="${generalItems.length}" class="ofp-group">ОФП</th>`
    }
    if (specialItems.length) {
        groupRow += `<th colspan="${specialItems.length}" class="sfp-group">СФП</th>`
    }
    groupRow += '<th></th></tr>'

    let subRow = '<tr class="sub-row"><th>№</th><th class="text-start">Спортсмен</th>'
    testItems.forEach(item => {
        subRow += `<th>${item.name}${item.unit ? `<br><span class="text-muted">${item.unit}</span>` : ''}</th>`
    })
    subRow += '<th>Итог<br><span class="text-muted">%</span></th></tr>'

    thead.innerHTML = groupRow + subRow
}

function renderTableBody(testItems, table) {
    const tbody = document.getElementById('examsTableBody')
    tbody.innerHTML = ''

    let index = 0
    for (const athleteId in table) {
        index += 1
        const row = table[athleteId]

        let cells = ''
        row.tests.forEach(test => {
            cells += renderResultCell(test)
        })

        const scoreClass = row.total_percent === null
            ? ''
            : row.total_percent >= (lastExamsData.pass_percent ?? 65) ? 'score-high' : 'score-mid'
        const scoreValue = row.total_percent === null ? '—' : row.total_percent

        tbody.insertAdjacentHTML('beforeend', `
            <tr data-name="${row.athlete.toLowerCase()}" data-athlete-id = "${athleteId}">
                <td>${index}</td>
                <td class="athlete-cell"><span class="athlete-avatar-placeholder"><i class="bi bi-person-fill"></i></span>${row.athlete}</td>
                ${cells}
                <td class="kpi-score ${scoreClass}">${scoreValue ?? 'не добавлено'}</td>
            </tr>
        `)
    }
    applyExamsSearch()
}

let examsSearchInput = document.getElementById('examsSearchInput')
if (examsSearchInput) {
    examsSearchInput.addEventListener('input', applyExamsSearch)
}

function applyExamsSearch() {
    if (!examsSearchInput) return
    let query = examsSearchInput.value.trim().toLowerCase()
    let tbody = document.getElementById('examsTableBody')
    if (!tbody) return
    tbody.querySelectorAll('tr').forEach(row => {
        let name = row.dataset.name || ''
        row.style.display = name.includes(query) ? '' : 'none'
    })
}

document.getElementById('examsTableBody').addEventListener('click', (event) => {
    let row = event.target.closest('tr[data-athlete-id]')

    if (!row) return

    selectedAthleteId = row.dataset.athleteId
    renderAthleteSidebar(selectedAthleteId)
})

function renderAthleteSidebar(athleteId) {
    const row = lastExamsData?.table[athleteId]
    if (!row) return
    const panel = document.getElementById('athleteSideCol')
    const wasClosed = !panel.classList.contains('is-open')
    selectedAthleteId = String(athleteId)
    panel.inert = false
    panel.classList.add('is-open')
    document.getElementById('sideAthleteName').textContent = row.athlete
    document.getElementById('sideInitial').textContent = row.athlete.trim().split(/\s+/).slice(0, 2).map(n => n[0]).join('')
    document.getElementById('sideAthleteMeta').textContent = `${groupSelect.selectedOptions[0]?.textContent || ''} · карточка спортсмена`
    const ids = Object.keys(lastExamsData.table)
    const index = ids.indexOf(String(athleteId))
    document.getElementById('sidePosition').textContent = `${index + 1} из ${ids.length}`
    document.getElementById('sidePrevBtn').disabled = index <= 0
    document.getElementById('sideNextBtn').disabled = index >= ids.length - 1
    dynamicsAllLeaders = false
    applySideTab()
    if (wasClosed) document.getElementById('sideAthleteName').focus({preventScroll: true})
}

for (const [id, offset] of [['sidePrevBtn', -1], ['sideNextBtn', 1]]) {
    document.getElementById(id).addEventListener('click', () => {
        const ids = Object.keys(lastExamsData?.table || {})
        const next = ids[ids.indexOf(String(selectedAthleteId)) + offset]
        if (next) renderAthleteSidebar(next)
    })
}

document.querySelectorAll('[data-side-tab]').forEach(link => {
    link.addEventListener('click', () => {
        activeSideTab = link.dataset.sideTab
        applySideTab()
    })
    link.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return
        event.preventDefault()
        const tabs = [...document.querySelectorAll('[data-side-tab]')]
        const index = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 :
            (tabs.indexOf(link) + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length
        tabs[index].focus()
        tabs[index].click()
    })
})

function applySideTab() {
    document.querySelectorAll('[data-side-tab]').forEach(link => {
        const selected = link.dataset.sideTab === activeSideTab
        link.classList.toggle('active', selected)
        link.setAttribute('aria-selected', String(selected))
        link.tabIndex = selected ? 0 : -1
    })
    for (const [tab, id] of [['results', 'sideSectionsContainer'], ['dynamics', 'sideDynamicsContainer']]) {
        document.getElementById(id).hidden = tab !== activeSideTab
    }
    if (selectedAthleteId) loadAthleteDynamics(selectedAthleteId)
}

// Динамика использует существующий URL; остальные разделы КПИ не меняются.
let dynamicsRequestId = 0
let dynamicsPeriodId = null
let dynamicsAllLeaders = false
const dynEscape = value => String(value ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
}[c]))
const dynNumber = value => Number.isFinite(value) ? value.toLocaleString('ru-RU', {maximumFractionDigits: 2}) : '—'
const dynValid = row => row && Number.isFinite(row.score) && ['passed', 'failed'].includes(row.result)
const dynStatus = row => ({
    passed: 'Сдал',
    failed: 'Не сдал',
    absent: 'Отсутствовал',
    exempted: 'Освобождён',
    empty: 'Не заполнено'
}[row?.result] || 'Нет записи')
const dynValue = (row, test) => dynValid(row) ? `${dynNumber(row.score)} ${dynEscape(test.unit)}` : '—'

async function loadAthleteDynamics(athleteId) {
    const container = document.getElementById('sideSummaryContainer')
    const groupId = groupSelect.value
    const key = `${groupId}:${athleteId}`
    const requestId = ++dynamicsRequestId
    const current = () => requestId === dynamicsRequestId && String(selectedAthleteId) === String(athleteId) && groupSelect.value === groupId
    if (dynamicsCache[key]) {
        renderDynamics(dynamicsCache[key])
        return
    }
    document.getElementById('sidePeriod').disabled = true
    document.getElementById('sidePeriod').innerHTML = '<option>Загрузка…</option>'
    document.getElementById('sideDataCount').textContent = ''
    for (const id of ['sideSectionsContainer', 'sideDynamicsContainer']) document.getElementById(id).replaceChildren()
    container.setAttribute('aria-busy', 'true')
    container.innerHTML = '<div class="dyn-empty" role="status">Загрузка динамики…</div>'
    try {
        const response = await fetch(`/teacher/fetch_athlete_dynamics/?${new URLSearchParams({
            group: groupId,
            athlete: athleteId
        })}`)
        if (!response.ok) throw new Error('Не удалось загрузить динамику. Попробуйте ещё раз.')
        const data = await response.json()
        if (!current()) return
        if (!data.success) throw new Error(data.error || 'Не удалось загрузить динамику')
        dynamicsCache[key] = data
        renderDynamics(data)
    } catch (error) {
        if (!current()) return
        container.innerHTML = `<div class="dyn-empty" role="alert">${dynEscape(error.message)}<br><button type="button" class="dyn-link" id="dynRetry">Повторить</button></div>`
        container.querySelector('#dynRetry').addEventListener('click', () => loadAthleteDynamics(athleteId))
    } finally {
        if (current()) container.removeAttribute('aria-busy')
    }
}

function renderDynamics(data) {
    const container = document.getElementById('sideDynamicsContainer')
    const summaryContainer = document.getElementById('sideSummaryContainer')
    summaryContainer.removeAttribute('aria-busy')
    if (!data.periods.length) {
        summaryContainer.innerHTML = '<div class="dyn-empty">Для этой группы пока нет КПИ.</div>'
        document.getElementById('sidePeriod').innerHTML = '<option>Нет КПИ</option>'
        document.getElementById('sidePeriod').disabled = true
        for (const id of ['sideSectionsContainer', 'sideDynamicsContainer']) document.getElementById(id).replaceChildren()
        return
    }
    let periodIndex = data.periods.findIndex(p => p.id === dynamicsPeriodId)
    if (periodIndex < 0) periodIndex = data.periods.length - 1
    const period = data.periods[periodIndex]
    dynamicsPeriodId = period.id
    const tests = data.tests.filter(t => period.test_ids.includes(t.id))
    if (!tests.some(t => t.id === dynamicsTestId)) dynamicsTestId = tests[0]?.id ?? null
    const test = tests.find(t => t.id === dynamicsTestId)
    const summary = period.summary
    const options = data.periods.map(p => `<option value="${p.id}" ${p.id === period.id ? 'selected' : ''}>${dynEscape(p.name)} · ${dynEscape(p.label)}${p.future ? ' · будущий' : ''}</option>`).join('')
    const rankFor = t => t.rankings[periodIndex].find(row => row.athlete_id === data.athlete_id)
    const groups = ['general', 'special'].map(type => ({
        title: type === 'general' ? 'ОФП' : 'СФП',
        items: tests.filter(t => (t.assessment_type === 'general' ? 'general' : 'special') === type)
    })).filter(group => group.items.length)
    const percentage = summary.total ? Math.round(summary.filled / summary.total * 100) : 0
    const periodSelect = document.getElementById('sidePeriod')
    periodSelect.disabled = false
    periodSelect.innerHTML = options
    document.getElementById('sideDataCount').textContent = `${tests.length} испытаний · ${data.students_count} спортсменов`
    summaryContainer.innerHTML = `
        ${period.future || period.invalid_dates ? `<div class="dyn-notice">${period.future ? 'Будущий КПИ. Показаны сохранённые результаты. ' : ''}${period.invalid_dates ? 'Дата окончания раньше даты начала — проверьте даты КПИ.' : ''}</div>` : ''}
        <div class="dyn-summary">
            <div class="dyn-summary-rank"><span>Общее место в группе</span><strong>${summary.rank ?? '—'} <small>${summary.rank ? `из ${summary.participants} участников` : ''}</small></strong><small>${summary.rank ? summary.ties > 1 ? `Делит место ещё с ${summary.ties - 1} участниками` : 'Без равных результатов' : 'Нет числовых результатов'}</small></div>
            <div><span>Сдано испытаний</span><strong>${summary.passed} <small>из ${summary.total}</small></strong><small>Все испытания · ОФП + СФП</small></div>
            <div><span>Полнота результатов</span><strong>${summary.filled} <small>из ${summary.total}</small></strong><div class="dyn-progress"><i style="width:${percentage}%"></i></div></div>
        </div>
        <div class="dyn-rank-note">Рейтинг предварительный · равные результаты делят место</div>
        <details class="dyn-rules"><summary>Как считаются места?</summary><p>Общее место — по количеству статусов «Сдал» среди участников с числовыми результатами. Место в испытании — по результату с учётом направления «меньше/больше — лучше». Равные результаты делят места: 1, 1, 3. Отсутствие и освобождение не участвуют в рейтинге. Рейтинг рассчитан для текущего состава группы.</p><p>Нормативы взяты из текущего справочника, статусы сдачи — из сохранённых результатов. Если пол не указан, показаны нормы М / Ж. Изменение считается относительно предыдущего числового замера того же испытания.</p></details>
        `
    renderSidebarResults(data, tests, periodIndex, groups)
    container.innerHTML = `${test ? `<div class="dyn-picker"><header><strong>Испытание</strong><small>${tests.length} в программе</small></header>
            <select id="dynTest" aria-label="Испытание для анализа">${groups.map(group => `<optgroup label="${group.title}">${group.items.map(t => `<option value="${t.id}" ${t.id === test.id ? 'selected' : ''}>${dynEscape(t.name)}</option>`).join('')}</optgroup>`).join('')}</select>
            <details id="dynAllTests"><summary>Все испытания и места</summary>${groups.map(group => `<div class="dyn-group-title"><span>${group.title}</span><span>${group.items.length} испытаний</span></div>${group.items.map(t => {
        const rank = rankFor(t)
        return `<button type="button" class="dyn-test-button" data-dyn-test="${t.id}" aria-pressed="${t.id === test.id}"><span>${dynEscape(t.name)}</span><span>${rank ? `${rank.rank} / ${t.rankings[periodIndex].length}` : '—'}</span></button>`
    }).join('')}`).join('')}</details></div><div id="dynDetail"></div>` : '<div class="dyn-empty">В этом КПИ пока нет испытаний.</div>'}`
    periodSelect.onchange = event => {
        dynamicsPeriodId = Number(event.target.value)
        dynamicsAllLeaders = false
        renderDynamics(data)
    }
    if (!test) return
    const selectTest = id => {
        const expanded = container.querySelector('#dynAllTests').open
        dynamicsTestId = id
        dynamicsAllLeaders = false
        renderDynamics(data)
        container.querySelector('#dynAllTests').open = expanded
    }
    container.querySelector('#dynTest').addEventListener('change', event => {
        selectTest(Number(event.target.value))
        container.querySelector('#dynTest').focus()
    })
    container.querySelectorAll('[data-dyn-test]').forEach(button => button.addEventListener('click', () => {
        selectTest(Number(button.dataset.dynTest))
        container.querySelector(`[data-dyn-test="${dynamicsTestId}"]`).focus()
    }))
    renderDynamicsDetail(data, test, periodIndex)
}

function renderSidebarResults(data, tests, index, groups) {
    const norm = t => `${t.better_direction === 'lower' ? '≤' : '≥'} ${Number.isFinite(t.norm) ? dynNumber(t.norm) : `${dynNumber(t.norm_male)} / ${dynNumber(t.norm_female)}`} ${dynEscape(t.unit)}`
    document.getElementById('sideSectionsContainer').innerHTML = tests.length ? `
        <div class="side-results-wrap"><table class="side-results" aria-label="Результаты выбранного КПИ">
        <thead><tr><th>Испытание</th><th>Результат</th><th>Норматив</th><th>Место</th><th>Статус</th></tr></thead><tbody>
        ${groups.map(group => `<tr class="side-category"><td colspan="5">${group.title}</td></tr>${group.items.map(test => {
        const row = test.values[index]
        const ranking = test.rankings[index]
        const mine = ranking.find(r => r.athlete_id === data.athlete_id)
        return `<tr><td>${dynEscape(test.name)}${dynamicsAchievementBadge(dynamicsAchievement(test, index))}</td><td>${dynValue(row, test)}</td><td>${norm(test)}</td><td>${mine ? `${mine.rank} / ${ranking.length}` : '—'}</td><td class="${row?.result === 'passed' ? 'dyn-good' : row?.result === 'failed' ? 'dyn-bad' : ''}">${dynStatus(row)}</td></tr>`
    }).join('')}`).join('')}</tbody></table></div>` : '<div class="dyn-empty">В этом КПИ пока нет испытаний.</div>'
}

// Сравнение только с более ранними КПИ того же испытания.
function dynamicsAchievement(test, index) {
    const current = test.values[index]
    const earlier = test.values.slice(0, index).filter(dynValid)
    if (!dynValid(current) || !earlier.length) return null
    const lower = test.better_direction === 'lower'
    const previous = earlier[earlier.length - 1]
    const best = earlier.reduce((a, b) => (lower ? b.score < a.score : b.score > a.score) ? b : a)
    const gain = lower ? previous.score - current.score : current.score - previous.score
    const recordGain = lower ? best.score - current.score : current.score - best.score
    return {
        gain, recordGain, previous: previous.score, best: best.score,
        improved: gain > 0, declined: gain < 0, record: recordGain > 0, tied: recordGain === 0
    }
}

function dynamicsAchievementBadge(achievement) {
    if (!achievement) return ''
    if (achievement.record) return '<span class="dyn-achievement-badge record">★ Личный рекорд</span>'
    if (achievement.tied) return '<span class="dyn-achievement-badge record">★ Повтор рекорда</span>'
    if (achievement.declined) return '<span class="dyn-achievement-badge declined">↘ Снижение</span>'
    if (achievement.improved) return '<span class="dyn-achievement-badge improved">↗ Улучшение</span>'
    return ''
}

function dynamicsAchievementBanner(test, index) {
    const a = dynamicsAchievement(test, index)
    if (!a || (!a.record && !a.tied && !a.improved && !a.declined)) return ''
    const record = a.record || a.tied
    const title = a.record ? 'Новый личный рекорд' : a.tied ? 'Личный рекорд повторён' : a.declined ? 'Результат снизился' : 'Результат улучшился'
    const value = dynValue(test.values[index], test)
    const delta = a.gain === 0 ? 'Без изменения к предыдущему замеру' :
        `${a.gain > 0 ? 'Лучше' : 'Хуже'} на ${dynNumber(Math.abs(a.gain))} ${dynEscape(test.unit)} к предыдущему замеру`
    return `<div class="dyn-achievement ${record ? 'record' : a.declined ? 'declined' : 'improved'}" role="status"><span class="dyn-achievement-icon" aria-hidden="true">${record ? '★' : a.declined ? '↘' : '↗'}</span><div><strong>${title}</strong><div class="dyn-achievement-value">${value}</div><div class="dyn-achievement-delta">${delta}</div></div></div>`
}

function renderDynamicsDetail(data, test, index) {
    const period = data.periods[index]
    const row = test.values[index]
    const history = data.periods.slice(0, index + 1).map((p, i) => ({
        period: p,
        row: test.values[i]
    })).filter(v => v.period.test_ids.includes(test.id))
    const filled = history.filter(v => dynValid(v.row))
    const previous = history.filter(v => v.period.id !== period.id && dynValid(v.row)).at(-1)
    const difference = dynValid(row) && previous ? Math.round((row.score - previous.row.score) * 100) / 100 : null
    const improved = difference !== null && (test.better_direction === 'lower' ? difference < 0 : difference > 0)
    const best = filled.length ? filled.reduce((a, b) => (test.better_direction === 'lower' ? b.row.score < a.row.score : b.row.score > a.row.score) ? b : a).row : null
    const ranking = test.rankings[index]
    const mine = ranking.find(r => r.athlete_id === data.athlete_id)
    const norms = Number.isFinite(test.norm) ? [test.norm] : [test.norm_male, test.norm_female].filter(Number.isFinite)
    const normText = `${test.better_direction === 'lower' ? '≤' : '≥'} ${Number.isFinite(test.norm) ? dynNumber(test.norm) : `${dynNumber(test.norm_male)} / ${dynNumber(test.norm_female)}`} ${dynEscape(test.unit)}`
    let leaders = ranking
    if (!dynamicsAllLeaders && ranking.length > 5) {
        leaders = ranking.slice(0, 4)
        leaders.push(mine && !leaders.includes(mine) ? mine : ranking[4])
    }
    document.getElementById('dynDetail').innerHTML = `
        <div class="dyn-title"><div><h3>${dynEscape(test.name)}</h3><p>${test.assessment_type === 'general' ? 'ОФП' : 'СФП'} · ${test.better_direction === 'lower' ? 'Меньше — лучше' : 'Больше — лучше'}</p></div><div class="dyn-rank-badge"><b>${mine ? `${mine.rank} из ${ranking.length}` : '—'}</b><span>место в испытании</span></div></div>
        ${dynamicsAchievementBanner(test, index)}
        <div class="dyn-chart-head"><strong>Динамика результата</strong><span>Замеров: ${filled.length}</span></div>
        <div class="dyn-chart-wrap">${dynamicsChart(test, history, norms)}</div>
        ${filled.length ? `<div class="dyn-legend"><span><i></i>Результат</span><span><i class="norm"></i>Норматив ${Number.isFinite(test.norm) ? '' : 'М / Ж '}из справочника</span></div>` : ''}
        <div class="dyn-metrics">
            <div><span>Результат выбранного КПИ</span><strong>${dynValue(row, test)}</strong><small class="${row?.result === 'passed' ? 'dyn-good' : row?.result === 'failed' ? 'dyn-bad' : ''}">${dynStatus(row)}</small></div>
            <div><span>К предыдущему замеру</span><strong class="${difference === null || difference === 0 ? '' : improved ? 'dyn-good' : 'dyn-bad'}">${difference === null ? '—' : `${difference > 0 ? '+' : ''}${dynNumber(difference)} ${dynEscape(test.unit)}`}</strong><small>${difference !== null ? `к ${dynEscape(previous.period.label)}` : dynValid(row) ? 'Нет предыдущего замера' : 'В выбранном КПИ нет замера'}</small></div>
            <div><span>Лучший до выбранного КПИ</span><strong>${dynValue(best, test)}</strong><small>Норма${Number.isFinite(test.norm) ? '' : ' М / Ж'}: ${normText}</small></div>
        </div>
        <div class="dyn-detail-note"><span>${dynEscape(period.label)} · ${dynStatus(row)}</span><span>${difference === null ? 'Недостаточно данных для оценки тренда' : difference === 0 ? 'Без изменения' : improved ? 'Результат улучшился' : 'Результат снизился'}</span></div>
        <div class="dyn-leader-head"><strong>Место среди участников</strong><small>${ranking.length} с замером из ${data.students_count}</small></div>
        <table class="dyn-leaders" aria-label="Рейтинг по выбранному испытанию"><thead><tr><th>Место</th><th>Спортсмен</th><th>Результат</th></tr></thead><tbody>${leaders.length ? leaders.map(r => `<tr class="${r.athlete_id === data.athlete_id ? 'selected' : ''}"><td>${r.rank}</td><td>${dynEscape(r.name)}${r.athlete_id === data.athlete_id ? '<small> выбран</small>' : ''}</td><td>${dynNumber(r.score)} ${dynEscape(test.unit)}</td></tr>`).join('') : '<tr><td colspan="3">В группе ещё нет числовых результатов.</td></tr>'}</tbody></table>
        ${ranking.length > 5 ? `<button type="button" class="dyn-link" id="dynLeadersToggle" aria-expanded="${dynamicsAllLeaders}">${dynamicsAllLeaders ? 'Свернуть рейтинг' : `Показать всех участников (${ranking.length})`}</button>` : ''}`
    document.getElementById('dynLeadersToggle')?.addEventListener('click', () => {
        dynamicsAllLeaders = !dynamicsAllLeaders
        renderDynamicsDetail(data, test, index)
        document.getElementById('dynLeadersToggle').focus()
    })
}

function dynamicsChart(test, history, norms) {
    const filled = history.filter(v => dynValid(v.row))
    if (!filled.length) return '<div class="dyn-empty">Пока нет результатов спортсмена<br>График появится после первого замера</div>'
    // Для длинной истории сохраняем читаемые подписи и горизонтальную прокрутку.
    const width = Math.max(310, history.length * 82), height = 208
    const left = 44, right = 32, top = 27, bottom = 36
    const values = [...filled.map(v => v.row.score), ...norms]
    const min = Math.min(...values), max = Math.max(...values)
    const pad = (max - min) * .25 || 1, lo = min - pad, hi = max + pad
    const x = i => history.length === 1 ? (left + width - right) / 2 : left + i * (width - left - right) / (history.length - 1)
    const y = value => top + (hi - value) / (hi - lo) * (height - top - bottom)
    let svg = `<svg viewBox="0 0 ${width} ${height}" style="min-width:${width}px" role="img" aria-label="${dynEscape(test.name)}: динамика результата"><title>${dynEscape(filled.map(v => `${v.period.label}: ${dynNumber(v.row.score)} ${test.unit}`).join('; '))}</title><text x="0" y="12">${dynEscape(test.unit)}</text>`
    ;[0, .5, 1].forEach(k => {
        const value = lo + (hi - lo) * k
        svg += `<line class="dyn-grid" x1="${left}" x2="${width - right}" y1="${y(value)}" y2="${y(value)}"/><text x="${left - 6}" y="${y(value) + 4}" text-anchor="end">${dynNumber(value)}</text>`
    })
    ;[...new Set(norms)].forEach(norm => {
        svg += `<line x1="${left}" x2="${width - right}" y1="${y(norm)}" y2="${y(norm)}" stroke="#a8b8cf" stroke-dasharray="4 4"><title>Норматив: ${dynNumber(norm)}</title></line>`
    })
    let path = '', pen = false
    history.forEach((v, i) => {
        if (!dynValid(v.row)) {
            pen = false;
            return
        }
        path += `${pen ? 'L' : 'M'}${x(i)} ${y(v.row.score)} `
        pen = true
    })
    svg += `<path d="${path}" fill="none" stroke="#3478ee" stroke-width="2.2"/>`
    history.forEach((v, i) => {
        const anchor = history.length === 1 ? 'middle' : i === 0 ? 'start' : i === history.length - 1 ? 'end' : 'middle'
        svg += `<text x="${x(i)}" y="${height - 12}" text-anchor="${anchor}">${dynEscape(v.period.label)}</text>`
        if (dynValid(v.row)) {
            svg += `<circle cx="${x(i)}" cy="${y(v.row.score)}" r="4.5" fill="#3478ee"><title>${dynEscape(v.period.label)}: ${dynNumber(v.row.score)} ${dynEscape(test.unit)} · ${dynStatus(v.row)}</title></circle><text x="${x(i)}" y="${y(v.row.score) - 12}" text-anchor="${anchor}" class="dyn-point-label">${dynNumber(v.row.score)}</text>`
        } else {
            svg += `<text x="${x(i)}" y="${top + 18}" text-anchor="${anchor}">Нет замера</text>`
        }
    })
    return svg + '</svg>'
}

document.getElementById('sideCloseBtn').addEventListener('click', hideAthleteSidebar)
document.getElementById('sideBackBtn').addEventListener('click', hideAthleteSidebar)
document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !document.querySelector('.modal.show')) hideAthleteSidebar()
})

function hideAthleteSidebar() {
    selectedAthleteId = null
    dynamicsRequestId += 1
    const panel = document.getElementById('athleteSideCol')
    if (panel?.contains(document.activeElement)) examsSearchInput?.focus({preventScroll: true})
    panel?.classList.remove('is-open')
    if (panel) panel.inert = true
}

// Рендерит одну ячейку результата испытания в зависимости от статуса сдачи
function renderResultCell(test) {
    if (test.result === 'empty') {
        return '<td class="text-muted">Не запол.</td>'
    }
    if (test.result === 'exempted') {
        return '<td class="text-muted">Освоб.</td>'
    }
    if (test.result === 'absent') {
        return '<td class="text-muted">Отсутс.</td>'
    }
    if (test.result === 'passed') {
        return `<td>${test.score ?? '-'} <i class="bi bi-check-circle-fill status-icon-ok"></i></td>`
    }
    // failed
    return `<td>${test.score ?? '-'} <i class="bi bi-x-circle-fill status-icon-fail"></i></td>`
}

// Режим станции
const stationModalEl = document.getElementById('stationModal')
const stationState = {
    assessmentId: null,
    testItems: [],
    selectedTestItemId: null,
    queue: [],
    pending: []
}

if (stationModalEl) {
    stationModalEl.addEventListener('show.bs.modal', () => {
        loadStationData(groupSelect.value)
    })
    stationModalEl.addEventListener('hidden.bs.modal', () => {
        fetchData()
    })
    document.getElementById('stationNextBtn').addEventListener('click', submitScore)
    document.getElementById('stationScoreInput').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') submitScore()

    })
    document.getElementById('stationAbsentBtn').addEventListener('click', () => submitQuickActions('absent'))
    document.getElementById('stationExemptedBtn').addEventListener('click', () => submitQuickActions('exempted'))
}

// Достает информацию по экзамену для заполнения результатов
// Если рез-ов нет, будет пустая модалка, если результат есть, то он будет показан на экране
function loadStationData(groupId, testItemId) {
    let params = {group: groupId}
    if (testItemId) params.test_item = testItemId
    let queryParams = buildQueryParams(params)

    fetch(`/teacher/fetch_station_data?${queryParams}`)
        .then((res) => {
            return res.json()
        })
        .then((data) => {
            if (!data.assessment_id) {
                document.getElementById('stationEmptyState').style.display = 'block'
                document.getElementById('stationContent').style.display = 'none'
                return
            }
            document.getElementById('stationEmptyState').style.display = 'none'
            document.getElementById('stationContent').style.display = 'flex'

            stationState.assessmentId = data.assessment_id
            stationState.testItems = data.test_items
            stationState.selectedTestItemId = data.selected_test_item

            document.getElementById('stationGroupTitle').textContent =
                groupSelect.selectedOptions[0] ? groupSelect.selectedOptions[0].textContent : ''
            renderStationPicker()
            setStationQueue(data.queue, data.selected_unit)
        })
        .catch(error => console.error(error))
}

// Отображает списокк упражнений для выбора(слева от списка спортсменов)
function renderStationPicker() {
    const picker = document.getElementById('stationPicker')
    picker.innerHTML = stationState.testItems.map((item, i) => {
        const complete = item.done >= item.total && item.total > 0
        return `
        <div class="station-item ${item.id === stationState.selectedTestItemId ? 'active' : ''}" data-id="${item.id}">
            <div class="idx">${i + 1}</div>
                <div class="info">
                    <div class="name">${item.name}</div>
                    <div class="meta">${item.assessment_type === 'general' ? 'ОФП' : 'СФП'} · ${item.unit}</div>
                </div>
            <div class="done-count ${complete ? 'complete' : ''}">${item.done}/${item.total}${complete ? ' ✓' : ''}</div>
        </div>
`
    }).join('')

    picker.querySelectorAll('.station-item').forEach(el => {
        el.addEventListener('click', () => {
            const testItemId = el.dataset.id
            stationState.selectedTestItemId = Number(testItemId)
            loadStationData(groupSelect.value, testItemId)
        })
    })
}

// Отображает текущее выбранное упражнение и вызывает следующие функции
function setStationQueue(queue, unit) {
    stationState.queue = queue
    stationState.pending = queue.filter(s => s.result === 'empty')

    const currentItem = stationState.testItems.find(t => t.id === stationState.selectedTestItemId)
    document.getElementById('stationTestName').textContent = currentItem ? currentItem.name : '-'
    document.getElementById('stationTestMeta').textContent = currentItem
        ? `${currentItem.assessment_type === 'general' ? 'ОФП' : 'СФП'} - ${unit}`
        : '-'
    document.getElementById('stationActiveUnit').textContent = unit || ''

    renderStationProgress()
    renderStationActive()
    renderStationQueueList()
}

// Показывает прогресс заполнения результатов спортсменов(сколько из общего кол-ва)
function renderStationProgress() {
    const total = stationState.queue.length
    const done = total - stationState.pending.length
    document.getElementById('stationProgressBadge').textContent = `${done} из ${total}`
}

// Показывает спортсмена из очереди. Нужна для заполнения результата
function renderStationActive() {
    const activeRow = document.getElementById('stationActiveRow')
    const quickActions = document.getElementById('stationQuickActions')
    const allDone = document.getElementById('stationAllDone')
    const next = stationState.pending[0]

    if (!next) {
        activeRow.style.display = 'none'
        quickActions.style.display = 'none'
        allDone.style.display = 'none'
        return
    }
    allDone.style.display = 'none'
    activeRow.style.display = 'flex'
    quickActions.style.display = 'flex'

    document.getElementById('stationActiveName').textContent = next.name
    const input = document.getElementById('stationScoreInput')
    input.value = ''
    input.focus()
}

// Функция отображения студентов в очереди
function renderStationQueueList() {
    const list = document.getElementById('stationQueueList')
    list.innerHTML = stationState.queue.map(s => {
        const isNext = stationState.pending[0] && stationState.pending[0].athlete_id === s.athlete_id
        const isUpcoming = s.result === 'empty' && !isNext
        return `
        <div class="station-list-row ${isNext ? 'current' : ''} ${isUpcoming ? 'upcoming' : ''}">
            <span class="athlete-avatar-placeholder"><i class="bi bi-person-fill"></i></span>
            <div><div class="name">${s.name}</div></div>
            ${renderStationResultPill(s)}
        </div>
            `
    }).join('')
}

// Функция отображения статуса в очереди
function renderStationResultPill(s) {
    if (s.result === 'empty') return '<div class="result-pill">- Ожидает</div>'
    if (s.result === 'absent') return '<div class="result-pill">Отсут.</div>'
    if (s.result === 'exempted') return '<div class="result-pill">Освоб.</div>'
    const icon = s.result === 'passed'
        ? '<i class="bi bi-check-circle-fill status-icon-ok"></i>'
        : '<i class="bi bi-x-circle-fill status-icon-fail"></i>'
    return `<div class="result-pill filled">${s.score ?? '-'} ${icon}</div>`
}

// Функция отправляющая запрос на сохранение результата
function submitStationResult(student, payload) {
    fetch('/teacher/add_exam_result/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            assessment_id: stationState.assessmentId,
            test_item_id: stationState.selectedTestItemId,
            athlete_id: student.athlete_id,
            ...payload
        })
    })
        .then(res => res.json())
        .then(data => {
            if (!data.success) {
                console.error(data.error)
                showToast({
                    type: 'warning',
                    title: 'Не допустимое значение',
                    message: data.error || 'Проверьте введенный результат'
                })
                return
            }
            student.result = data.result
            student.score = data.score
            stationState.pending = stationState.queue.filter(s => s.result === 'empty')

            const item = stationState.testItems.find(t => t.id === stationState.selectedTestItemId)
            if (item) item.done += 1

            showToast({
                type: 'success',
                title: 'Результат сохранен'
            })

            renderStationPicker()
            renderStationProgress()
            renderStationActive()
            renderStationQueueList()
        })
        .catch(error => {
            console.error(error)
            showToast({
                type: 'error',
                title: 'Ошибка',
                message: 'Нет соединения с сервером, проверьте подключение'
            })
        })
}

// Функция отправки результата о освобождение или отсутствии
function submitQuickActions(action) {
    const next = stationState.pending[0]

    if (!next) return
    submitStationResult(next, {action})
}

// Функция отправки резкльтата о сдачи или не сдачи
function submitScore() {
    const next = stationState.pending[0]

    if (!next) return
    const input = document.getElementById('stationScoreInput')
    const value = input.value.trim().replace(',', '.')

    if (value === '' || isNaN(Number(value))) {
        input.focus()
        return
    }
    submitStationResult(next, {action: 'score', score: Number(value)})

}

function showToast({type = 'success', title, message, duration = 4000}) {
    const container = document.getElementById('att-toast-container')
    if (!container) return

    const icons = {
        success: 'bi bi-check-circle-fill',
        error: 'bi bi-x-circle-fill',
        warning: 'bi bi-exclamation-circle-fill'
    }
    const toast = document.createElement('div')
    toast.className = `att-toast ${type}`
    toast.style.position = 'relative'
    toast.innerHTML = `
            <div class="att-toast-icon ${type}"><i class="${icons[type]}"></i></div>
            <div class="att-toast-body">
                <p class="att-toast-title">${title}</p>
                ${message ? `<p class="att-toast-msg">${message}</p>` : ''}
            </div>
            <button class="att-toast-close" aria-label="Закрыть"><i class="bi bi-x"></i></button>
            <div class="att-toast-progress" style="width:100%"></div>
        `
    container.appendChild(toast)
    requestAnimationFrame(() => requestAnimationFrame(() => toast.classList.add('show')))

    const progress = toast.querySelector('.att-toast-progress')
    progress.style.transition = `width ${duration}ms linear`
    requestAnimationFrame(() => requestAnimationFrame(() => {
        progress.style.width = '0%'
    }))

    const dismiss = () => {
        toast.classList.remove('show')
        toast.classList.add('hide')
        setTimeout(() => toast.remove(), 400)
    }
    toast.querySelector('.att-toast-close').addEventListener('click', dismiss)
    const timer = setTimeout(dismiss, duration)
    toast.addEventListener('mouseenter', () => clearTimeout(timer))
    toast.addEventListener('mouseleave', () => setTimeout(dismiss, 1500))
}

// Экспорт в excel
document.getElementById('exportExcelBtn').addEventListener('click', () => {
    window.location.href = `/teacher/export_exams_excel/?${buildQueryParams({group: groupSelect.value})}`
})
