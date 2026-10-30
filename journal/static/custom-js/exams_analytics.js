// Вкладка "Аналитика по испытаниям" (exams.html -> #tabAnalytics, модалка #anDetailModal)
// Зависит от exams.js: groupSelect, buildQueryParams.

// Порог сдачи КПИ. Должен совпадать с KPI_PASS_PERCENT в teacher/utils.py
const AN_PASS_PERCENT = 65

const AN_LABELS = {
    passed: 'Сдал', failed: 'Не сдал', absent: 'Отсутствовал',
    exempted: 'Освобождён', empty: 'Нет результата'
}

let anData = null        // ответ fetch_exams_analytics
let anLoaded = false     // данные актуальны для текущей группы
let anActive = false     // вкладка открыта
let anRequestId = 0      // защита от гонки запросов
let anAssessmentId = null  // конкретный КПИ (из «Истории группы»); null = последний
let anTestId = null      // испытание, открытое в модалке

const $an = id => document.getElementById(id)

const anEsc = v => String(v ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[c]))

const anFmt = v => v === null || v === undefined
    ? '—' : Number(Number(v).toFixed(2)).toLocaleString('ru-RU')

// есть числовой замер
const anMeasured = r => r.score !== null && r.score !== undefined && ['passed', 'failed'].includes(r.result)

// почему не сдал / сколько не хватает
function anGapText(t, r) {
    if (r.norm === null || r.norm === undefined) return 'норматив не задан (проверьте пол спортсмена)'
    if (r.gap !== null) return `не хватает: ${anFmt(r.gap)} ${anEsc(t.unit)}`
    return 'вне допустимого диапазона'
}

const anSign = t => t.better_direction === 'lower' ? '≤' : '≥'

// ---------- переключение вкладок (results / analytics / compare) ----------
const AN_PANELS = {results: 'tabResults', analytics: 'tabAnalytics', compare: 'tabCompare', history: 'tabHistory'}

document.querySelectorAll('[data-main-tab]').forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault()
        const tab = link.dataset.mainTab
        anActive = tab === 'analytics'
        document.querySelectorAll('[data-main-tab]').forEach(l => l.classList.toggle('active', l === link))
        Object.entries(AN_PANELS).forEach(([name, id]) => $an(id)?.classList.toggle('d-none', name !== tab))
        if (anActive) loadAnalytics()
        window.dispatchEvent(new CustomEvent('main-tab', {detail: tab}))  // exams_compare.js слушает это событие
    })
})

// вид подготовки: ОФП / СФП
$an('kindSelect')?.addEventListener('change', () => {
    if (anActive && anData) renderAnalytics()
})

// вызывается из exams.js после перезагрузки данных (смена группы, новый результат)
window.refreshAnalytics = () => {
    anAssessmentId = null
    anLoaded = false
    if (anActive) loadAnalytics()
}

// ---------- загрузка ----------
// ===== ИСТОЧНИК ДАННЫХ =====
// Сейчас возвращает заглушку AN_STUB (внизу файла).
// Чтобы подключить настоящие данные: удалите строку "return AN_STUB"
// и раскомментируйте блок ниже. Остальной код трогать не нужно.
// assessmentId - id КПИ из «Истории группы» (null = последний КПИ группы)
async function getAnalyticsData(assessmentId) {


    const params = {group: groupSelect.value, ...periodParam()}   // по умолчанию - КПИ, выбранный вверху страницы
    if (assessmentId) params.assessment = assessmentId
    const res = await fetch(`/teacher/fetch_exams_analytics/?${buildQueryParams(params)}`)
    return await res.json()
}

// «Открыть →» из истории группы: показать аналитику выбранного КПИ
window.openAnalyticsFor = assessmentId => {
    anAssessmentId = assessmentId
    anLoaded = false
    document.querySelector('[data-main-tab="analytics"]').click()
}

function loadAnalytics() {
    if (anLoaded && anData) return renderAnalytics()
    const id = ++anRequestId
    getAnalyticsData(anAssessmentId)
        .then(data => {
            if (id !== anRequestId) return   // пришёл ответ для уже сменённой группы
            anData = data
            anLoaded = true
            renderAnalytics()
        })
        .catch(err => console.error(err))
}

function anKindTests() {
    const text = $an('kindSelect')?.value || ''
    const kind = text.startsWith('ОФП +') ? 'all' : text === 'ОФП' ? 'general' : text === 'СФП' ? 'special' : 'all'
    return anData.tests.filter(t => kind === 'all' || (kind === 'general' ? t.type === 'general' : t.type !== 'general'))
}

// ---------- карточки и таблица ----------
function anAthletes(tests) {
    const map = new Map()
    tests.forEach(t => t.rows.forEach(r => {
        if (!map.has(r.athlete_id)) map.set(r.athlete_id, {name: r.name, entries: []})
        map.get(r.athlete_id).entries.push({t, r})
    }))
    return [...map.values()].map(a => {
        const failed = a.entries.filter(e => e.r.result === 'failed')
        const pending = a.entries.filter(e => ['absent', 'empty'].includes(e.r.result))
        const passed = a.entries.filter(e => e.r.result === 'passed').length
        const required = a.entries.filter(e => e.r.result !== 'exempted').length  // освобождённые не считаются
        const percent = required ? Math.round(passed / required * 100) : 0
        // правило КПИ (как в шапке): >= 65% сданных испытаний = сдал
        let status = 'pending'
        if (percent >= AN_PASS_PERCENT) status = 'passed'
        else if (failed.length) status = 'failed'
        return {...a, failed, pending, passed, required, percent, status}
    })
}

function anEntry({t, r}) {
    const norm = r.norm === null || r.norm === undefined ? '' : ` · норма ${anSign(t)} ${anFmt(r.norm)} ${anEsc(t.unit)}`
    let meta
    if (anMeasured(r)) meta = `Результат: ${anFmt(r.score)} ${anEsc(t.unit)}${norm}`
    else meta = `${AN_LABELS[r.result]}${norm}`

    let extra = ''
    if (r.result === 'failed') {
        extra = `<span class="an-test-meta an-red">Не сдано · ${anGapText(t, r)}</span>`
    } else if (r.result === 'passed') {
        extra = '<span class="an-test-meta an-green">Сдано</span>'
    }
    return `<li><span class="an-test-name">${anEsc(t.name)}</span><span class="an-test-meta">${meta}</span>${extra}</li>`
}

function anFillList(id, athletes, entriesOf) {
    $an(id).innerHTML = athletes.length
        ? athletes.map(a => {
            const items = entriesOf(a)
            return `<li><b>${anEsc(a.name)}</b> <span class="an-pct">${a.percent}% · ${a.passed} из ${a.required}</span>
                <ul class="an-athlete-tests">${items.length ? items.map(anEntry).join('') : '<li class="an-test-meta an-green">Все испытания сданы</li>'}</ul></li>`
        }).join('')
        : '<li class="an-empty">В этой категории спортсменов нет.</li>'
}

function renderAnalytics() {
    if (!anData.assessment) {
        $an('anTableBody').innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">Для этой группы пока нет КПИ</td></tr>'
        ;['anCompleteCount', 'anFailedCount', 'anPendingCount', 'anTotalCount'].forEach(id => $an(id).textContent = 0)
        ;['anCompleteList', 'anFailedList', 'anPendingList'].forEach(id => $an(id).innerHTML = '<li class="an-empty">Нет данных.</li>')
        $an('anTableSub').textContent = ''
        return
    }

    const tests = anKindTests()
    const athletes = anAthletes(tests)
    const complete = athletes.filter(a => a.status === 'passed')
    const failed = athletes.filter(a => a.status === 'failed')
    const pending = athletes.filter(a => a.status === 'pending')

    $an('anTotalCount').textContent = athletes.length
    $an('anCompleteCount').textContent = complete.length
    $an('anFailedCount').textContent = failed.length
    $an('anPendingCount').textContent = pending.length

    anFillList('anCompleteList', complete, a => [...a.failed, ...a.pending])
    anFillList('anFailedList', failed, a => [...a.failed, ...a.pending])
    anFillList('anPendingList', pending, a => a.pending)

    // сначала испытания с наибольшей долей несдавших среди замеров
    const share = t => t.counts.failed / ((t.counts.passed + t.counts.failed) || 1)
    const sorted = [...tests].sort((a, b) => share(b) - share(a))

    $an('anTableSub').textContent = `${anData.assessment.name} · сначала наибольшая доля несдавших среди замеров`
    $an('anTableBody').innerHTML = sorted.length ? sorted.map(t => {
        const c = t.counts
        return `<tr>
            <td class="text-start"><b>${anEsc(t.name)}</b><div class="an-sub">${t.type === 'general' ? 'ОФП' : 'СФП'}</div></td>
            <td>${c.passed}</td><td>${c.failed}</td><td>${c.absent + c.exempted + c.empty}</td>
            <td><button type="button" class="btn btn-link btn-sm p-0" data-an-detail="${t.id}">Подробнее <i class="bi bi-arrow-right"></i></button></td>
        </tr>`
    }).join('') : '<tr><td colspan="5" class="text-center text-muted py-4">Нет испытаний</td></tr>'
}

// кнопка "Подробнее" (делегирование: строки пересоздаются)
$an('anTableBody')?.addEventListener('click', e => {
    const btn = e.target.closest('[data-an-detail]')
    if (btn) openDetail(Number(btn.dataset.anDetail))
})

// ---------- модалка "Подробнее" ----------
function openDetail(testId) {
    anTestId = testId
    const t = anData.tests.find(x => x.id === testId)
    if (!t) return
    $an('anDetailTitle').textContent = t.name
    $an('anDetailSub').textContent =
        `${anData.assessment.name} · ${t.unit} · ${t.better_direction === 'lower' ? 'Меньше — лучше' : 'Больше — лучше'}`
    $an('anGender').value = 'all'
    $an('anSearch').value = ''
    $an('anStatus').value = 'all'
    renderLeaders()
    renderDetailRows()
    bootstrap.Modal.getOrCreateInstance($an('anDetailModal')).show()
}

const anStatusBadge = s => `<span class="an-status an-status-${s}">${AN_LABELS[s]}</span>`

// топ-3: одинаковые результаты делят место, призёров может быть больше трёх
function renderLeaders() {
    const t = anData.tests.find(x => x.id === anTestId)
    const g = $an('anGender').value
    const ranked = t.rows
        .filter(r => anMeasured(r) && (g === 'all' || r.gender === g))
        .sort((a, b) => (a.score - b.score) * (t.better_direction === 'lower' ? 1 : -1) || a.name.localeCompare(b.name, 'ru'))
    let prev = null, place = 0
    const top = ranked.map((r, i) => {
        if (i === 0 || r.score !== prev) place = i + 1
        prev = r.score
        return {...r, place}
    }).filter(r => r.place <= 3)

    $an('anLeaders').innerHTML = top.length
        ? top.map(r => `<li><span class="an-place">${r.place}</span>
            <span class="an-leader-name">${anEsc(r.name)} ${anStatusBadge(r.result)}</span>
            <b>${anFmt(r.score)} ${anEsc(t.unit)}</b></li>`).join('')
        : '<li class="an-empty">В этой категории пока нет результатов с замером.</li>'
}

function renderDetailRows() {
    const t = anData.tests.find(x => x.id === anTestId)
    const q = $an('anSearch').value.trim().toLowerCase()
    const st = $an('anStatus').value
    const rows = t.rows.filter(r => (st === 'all' || r.result === st) && (!q || r.name.toLowerCase().includes(q)))

    $an('anDetailRows').innerHTML = rows.length ? rows.map(r => {
        let gap = '—'
        if (r.result === 'passed' && anMeasured(r)) gap = 'Норматив выполнен'
        else if (r.result === 'failed') gap = anGapText(t, r)
        return `<tr>
            <td class="text-start">${anEsc(r.name)}</td>
            <td>${anMeasured(r) ? `${anFmt(r.score)} ${anEsc(t.unit)}` : '—'}</td>
            <td>${r.norm === null || r.norm === undefined ? '—' : `${anSign(t)} ${anFmt(r.norm)} ${anEsc(t.unit)}`}</td>
            <td>${gap}</td>
            <td>${anStatusBadge(r.result)}</td>
        </tr>`
    }).join('') : '<tr><td colspan="5" class="text-center text-muted py-3">Ничего не найдено</td></tr>'
}

$an('anGender')?.addEventListener('change', renderLeaders)
$an('anSearch')?.addEventListener('input', renderDetailRows)
$an('anStatus')?.addEventListener('change', renderDetailRows)

// ===== ЗАГЛУШКА: удалить вместе со строкой "return AN_STUB" =====
// Формат данных - такой же, как возвращает fetch_exams_analytics.
//
// Формат:
// {
//   assessment: {name, date_start, date_end} | null,
//   student_count: int,
//   tests: [{
//     id, name, type: 'general'|'special', unit, better_direction: 'lower'|'higher',
//     counts: {passed, failed, absent, exempted, empty},
//     rows: [{athlete_id, name, gender: 'male'|'female'|null,
//             result: 'passed'|'failed'|'absent'|'exempted'|'empty', score, norm, gap}]
//   }]
// }
const AN_STUB = (() => {
    const athletes = [
        ['Иванов Иван Иванович', 'male'], ['Петров Пётр Петрович', 'male'],
        ['Сидоров Сидор Сидорович', 'male'], ['Козлов Андрей Сергеевич', 'male'],
        ['Смирнова Анна Павловна', 'female'], ['Кузнецова Мария Ивановна', 'female'],
        ['Попова Елена Андреевна', 'female'], ['Васильева Ольга Дмитриевна', 'female'],
    ]
    // [id, название, тип, ед., направление, норма м, норма ж, результаты по спортсменам]
    // число = балл; 'a' = отсутствовал, 'e' = освобождён, null = нет результата
    const defs = [
        [1, 'Бег 30 м', 'general', 'сек.', 'lower', 5.2, 5.8, [5.0, 5.4, 5.1, 6.0, 5.9, 5.7, 'a', 6.3]],
        [2, 'Прыжок в длину с места', 'general', 'см.', 'higher', 200, 170, [210, 195, 'e', 205, 175, 160, 172, 168]],
        [3, 'Подъём ног', 'special', 'кол-во.повт.', 'higher', 12, 10, [14, 12, 11, 12, 10, 8, 11, null]],
        [4, 'Мостик', 'special', 'сек.', 'higher', 30, 25, [35, 28, 31, 32, 26, 24, 27, 'a']],
    ]
    const tests = defs.map(([id, name, type, unit, dir, nm, nf, vals]) => {
        const counts = {passed: 0, failed: 0, absent: 0, exempted: 0, empty: 0}
        const rows = athletes.map(([fio, gender], i) => {
            const norm = gender === 'male' ? nm : nf
            const v = vals[i]
            let result, score = null, gap = null
            if (v === 'a') result = 'absent'
            else if (v === 'e') result = 'exempted'
            else if (v === null) result = 'empty'
            else {
                score = v
                result = (dir === 'lower' ? v <= norm : v >= norm) ? 'passed' : 'failed'
                if (result === 'failed') gap = Math.round((dir === 'lower' ? v - norm : norm - v) * 100) / 100
            }
            counts[result]++
            return {athlete_id: i + 1, name: fio, gender, result, score, norm, gap}
        })
        return {id, name, type, unit, better_direction: dir, counts, rows}
    })
    return {
        assessment: {name: 'КПИ Осень 2026', date_start: '01.09.2026', date_end: '30.09.2026'},
        student_count: athletes.length,
        tests,
    }
})()
