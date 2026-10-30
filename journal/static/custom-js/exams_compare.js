// Вкладка "Сравнение периодов" (exams.html -> #tabCompare, модалка #cmpDetailModal)
// Зависит от exams.js: groupSelect, buildQueryParams. Вкладками управляет exams_analytics.js.

// ===== ИСТОЧНИК ДАННЫХ =====
// Сейчас возвращает заглушку CMP_STUB (внизу файла).
// Чтобы подключить настоящие данные: удалите строку "return CMP_STUB"
// и раскомментируйте блок ниже. Остальной код трогать не нужно.
async function getComparisonData() {

    const res = await fetch(`/teacher/fetch_exams_comparison/?${buildQueryParams({group: groupSelect.value})}`)
    return await res.json()
}

let cmpData = null        // ответ fetch_exams_comparison
let cmpLoaded = false     // данные актуальны для текущей группы
let cmpActive = false     // вкладка открыта
let cmpRequestId = 0      // защита от гонки запросов
let cmpA = 0              // индекс периода "С чем сравнить"
let cmpB = 0              // индекс периода "Какой оценить"

const $c = id => document.getElementById(id)

const cmpEsc = v => String(v ?? '').replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[ch]))

const cmpFmt = v => v === null || v === undefined
    ? '—' : Number(Number(v).toFixed(2)).toLocaleString('ru-RU')

const cmpAvg = list => list.length ? list.reduce((s, x) => s + x, 0) / list.length : null

// ---------- события ----------
window.addEventListener('main-tab', e => {
    cmpActive = e.detail === 'compare'
    if (cmpActive) loadComparison()
})

// вызывается из exams.js после перезагрузки данных (смена группы, новый результат)
window.refreshCompare = () => {
    cmpLoaded = false
    if (cmpActive) loadComparison()
}

$c('kindSelect')?.addEventListener('change', () => {
    if (cmpActive && cmpData) renderComparison()
})

$c('cmpPeriodA')?.addEventListener('change', e => { cmpA = Number(e.target.value); renderComparison() })
$c('cmpPeriodB')?.addEventListener('change', e => { cmpB = Number(e.target.value); renderComparison() })
$c('cmpSwap')?.addEventListener('click', () => {
    [cmpA, cmpB] = [cmpB, cmpA]
    renderComparison()
})

// кнопка "По спортсменам" (делегирование: строки пересоздаются)
$c('cmpTableBody')?.addEventListener('click', e => {
    const btn = e.target.closest('[data-cmp-detail]')
    if (btn) openCompareDetail(btn.dataset.cmpDetail)
})

// «Сравнить с предыдущим периодом» из истории группы: B = выбранный КПИ, A = предыдущий
window.openCompareFor = async periodId => {
    if (!cmpData) cmpData = await getComparisonData()
    cmpLoaded = true
    const i = cmpData.periods.findIndex(p => p.id === periodId)
    cmpB = Math.max(i, 0)
    cmpA = Math.max(i - 1, 0)
    document.querySelector('[data-main-tab="compare"]').click()
}

// ---------- загрузка ----------
function loadComparison() {
    if (cmpLoaded && cmpData) return renderComparison()
    const id = ++cmpRequestId
    getComparisonData()
        .then(data => {
            if (id !== cmpRequestId) return   // ответ для уже сменённой группы
            cmpData = data
            cmpLoaded = true
            // по умолчанию: два последних КПИ (предыдущий -> последний)
            const last = data.periods.length - 1
            cmpB = Math.max(last, 0)
            cmpA = Math.max(last - 1, 0)
            renderComparison()
        })
        .catch(err => console.error(err))
}

// ---------- расчёты ----------
function cmpKindTests() {
    const text = $c('kindSelect')?.value || ''
    const kind = text.startsWith('ОФП +') ? 'all' : text === 'ОФП' ? 'general' : text === 'СФП' ? 'special' : 'all'
    return cmpData.tests.filter(t => kind === 'all' || (kind === 'general' ? t.type === 'general' : t.type !== 'general'))
}

const cmpMeasured = v => v && v.score !== null && v.score !== undefined && ['passed', 'failed'].includes(v.result)

// спортсмены, у которых есть замер в ОБОИХ периодах
function cmpPairs(test) {
    const idA = String(cmpData.periods[cmpA]?.id)
    const idB = String(cmpData.periods[cmpB]?.id)
    return test.rows
        .filter(r => cmpMeasured(r.values[idA]) && cmpMeasured(r.values[idB]))
        .map(r => ({name: r.name, a: r.values[idA].score, b: r.values[idB].score}))
}

function cmpScores(test, periodId) {
     return test.rows.filter((r)=>cmpMeasured(r.values[String(periodId)])).map((r)=>r.values[String(periodId)].score)
}

// разница B - A; good = true, если стало лучше с учётом направления (lower/higher)
function cmpDelta(test, a, b) {
    if (a === null || b === null) return {d: null, good: false}
    const d = b - a
    return {d, good: d * (test.better_direction === 'lower' ? -1 : 1) > 0}
}

function cmpDeltaHtml(test, a, b) {
    const {d, good} = cmpDelta(test, a, b)
    if (d === null) return 'Нет данных'
    if (d === 0) return 'Без изменений'
    return `<b>${good ? 'Лучше' : 'Хуже'} на ${cmpFmt(Math.abs(d))} ${cmpEsc(test.unit)}</b>`
}

// ---------- отрисовка ----------
function renderComparison() {
    if (!cmpData.periods.length) {
        $c('cmpSummary').className = 'cmp-summary cmp-notice'
        $c('cmpSummary').textContent = 'Для этой группы пока нет КПИ.'
        $c('cmpTableBody').innerHTML = ''
        return
    }

    // селекты периодов
    const options = cmpData.periods.map((p, i) =>
        `<option value="${i}">${cmpEsc(p.name)} · ${cmpEsc(p.date_start)}</option>`).join('')
    $c('cmpPeriodA').innerHTML = options
    $c('cmpPeriodB').innerHTML = options
    $c('cmpPeriodA').value = cmpA
    $c('cmpPeriodB').value = cmpB

    const nameA = cmpData.periods[cmpA].name
    const nameB = cmpData.periods[cmpB].name
    $c('cmpHeadA').textContent = nameA
    $c('cmpHeadB').textContent = nameB

    const tests = cmpKindTests()
    let total = 0, improved = 0, worse = 0, anyData = false
    const rows = tests.map(t => {
        const pairs = cmpPairs(t)
        pairs.forEach(p => {
            const {d, good} = cmpDelta(t, p.a, p.b)
            total++
            if (d !== 0) good ? improved++ : worse++
        })
        const idA = cmpData.periods[cmpA].id, idB = cmpData.periods[cmpB].id
        const onlyA = cmpScores(t, idA), onlyB = cmpScores(t, idB)
        const hasData = onlyA.length > 0 || onlyB.length > 0
        if (hasData) anyData = true

        // есть пары: средние по одним и тем же спортсменам; пар нет: показываем, что есть за каждый период
        const a = pairs.length ? cmpAvg(pairs.map(p => p.a)) : cmpAvg(onlyA)
        const b = pairs.length ? cmpAvg(pairs.map(p => p.b)) : cmpAvg(onlyB)
        const {d, good} = cmpDelta(t, pairs.length ? a : null, pairs.length ? b : null)
        const cls = d === null || d === 0 ? '' : good ? 'cmp-good' : 'cmp-bad'
        // нет пар, но данные есть хотя бы за один период -> «Нет изменений»; данных нет совсем -> «Нет данных»
        const changeHtml = pairs.length ? cmpDeltaHtml(t, a, b) : hasData ? 'Нет изменений' : 'Нет данных'
        let note = `Замеров в обоих периодах: ${pairs.length}`
        if (!pairs.length && hasData) {
            note += onlyA.length && !onlyB.length ? ` · данные только за «${cmpEsc(nameA)}»`
                : onlyB.length && !onlyA.length ? ` · данные только за «${cmpEsc(nameB)}»`
                : ' · у разных спортсменов'
        }
        return `<tr>
            <td class="text-start"><b>${cmpEsc(t.name)}</b><div class="an-sub">${note}</div></td>
            <td>${a === null ? '—' : `${cmpFmt(a)} ${cmpEsc(t.unit)}`}</td>
            <td>${b === null ? '—' : `${cmpFmt(b)} ${cmpEsc(t.unit)}`}</td>
            <td class="${cls}">${changeHtml}</td>
            <td><button type="button" class="btn btn-link btn-sm p-0" data-cmp-detail="${cmpEsc(t.key)}">По спортсменам <i class="bi bi-box-arrow-up-right"></i></button></td>
        </tr>`
    })
    $c('cmpTableBody').innerHTML = rows.length ? rows.join('')
        : '<tr><td colspan="5" class="text-center text-muted py-4">Нет испытаний</td></tr>'

    // итоговая строка
    const summary = $c('cmpSummary')
    if (cmpA === cmpB) {
        summary.className = 'cmp-summary cmp-notice'
        summary.textContent = 'Выберите разные периоды, чтобы увидеть изменения.'
    } else if (total === 0 && anyData) {
        summary.className = 'cmp-summary cmp-notice'
        summary.textContent = 'Нет спортсменов с замером в обоих периодах: показаны имеющиеся результаты, изменений нет.'
    } else {
        summary.className = 'cmp-summary'
        summary.innerHTML = `Из <strong>${total}</strong> пар результатов: <strong>${improved}</strong> лучше, <strong>${worse}</strong> хуже, <strong>${total - improved - worse}</strong> без изменений.`
    }
}

// ---------- модалка "По спортсменам" ----------
function openCompareDetail(key) {
    const t = cmpData.tests.find(x => x.key === key)
    if (!t) return
    const nameA = cmpData.periods[cmpA].name
    const nameB = cmpData.periods[cmpB].name

    $c('cmpDetailTitle').textContent = t.name
    $c('cmpDetailSub').textContent =
        `${nameA} → ${nameB} · ${t.unit} · ${t.better_direction === 'lower' ? 'Меньше — лучше' : 'Больше — лучше'}`
    $c('cmpDetailHeadA').textContent = nameA
    $c('cmpDetailHeadB').textContent = nameB

    // все спортсмены, у которых есть замер хотя бы в одном из периодов
    const idA = String(cmpData.periods[cmpA].id), idB = String(cmpData.periods[cmpB].id)
    const rows = t.rows
        .map(r => ({
            name: r.name,
            a: cmpMeasured(r.values[idA]) ? r.values[idA].score : null,
            b: cmpMeasured(r.values[idB]) ? r.values[idB].score : null,
        }))
        .filter(r => r.a !== null || r.b !== null)

    $c('cmpDetailRows').innerHTML = rows.length ? rows.map(r => {
        let change
        if (r.a !== null && r.b !== null) {
            const {d, good} = cmpDelta(t, r.a, r.b)
            const cls = d === 0 ? '' : good ? 'cmp-good' : 'cmp-bad'
            const text = d === 0 ? 'без изменений' : good ? 'лучше' : 'хуже'
            change = `<td class="${cls}">${d > 0 ? '+' : ''}${cmpFmt(d)} ${cmpEsc(t.unit)} · ${text}</td>`
        } else {
            change = '<td>Нет изменений</td>'   // замер только в одном периоде
        }
        return `<tr>
            <td class="text-start">${cmpEsc(r.name)}</td>
            <td>${cmpFmt(r.a)}</td>
            <td>${cmpFmt(r.b)}</td>
            ${change}
        </tr>`
    }).join('') : '<tr><td colspan="4" class="text-center text-muted py-3">Нет результатов с замером в этих периодах</td></tr>'

    bootstrap.Modal.getOrCreateInstance($c('cmpDetailModal')).show()
}

// ===== ЗАГЛУШКА: удалить вместе со строкой "return CMP_STUB" =====
// Формат такой же, как возвращает fetch_exams_comparison:
// {
//   periods: [{id, name, date_start, date_end}],            // по возрастанию даты
//   tests: [{key, name, type: 'general'|'special', unit, better_direction: 'lower'|'higher',
//            rows: [{athlete_id, name, values: {<id периода>: {score, result}}}]}]
// }
const CMP_STUB = (() => {
    const periods = [
        {id: 1, name: 'Февраль 2026', date_start: '10.02.2026', date_end: '20.02.2026'},
        {id: 2, name: 'Май 2026', date_start: '12.05.2026', date_end: '22.05.2026'},
        {id: 3, name: 'Октябрь 2026', date_start: '01.10.2026', date_end: '10.10.2026'},
    ]
    const athletes = [
        'Иванов Иван Иванович', 'Петров Пётр Петрович', 'Сидоров Сидор Сидорович', 'Козлов Андрей Сергеевич',
        'Смирнова Анна Павловна', 'Кузнецова Мария Ивановна', 'Попова Елена Андреевна', 'Васильева Ольга Дмитриевна',
    ]
    // [key, название, тип, ед., направление, [баллы по периодам для каждого спортсмена]]
    // null = нет замера (пропуск / не заполнено)
    const defs = [
        ['general:бег 30 м', 'Бег 30 м', 'general', 'сек.', 'lower', [
            [5.6, 5.4, 5.2], [5.9, 5.7, 5.8], [5.5, 5.5, 5.3], [6.2, 6.0, 5.9],
            [6.1, 5.9, 5.8], [6.3, null, 6.0], [6.0, 5.8, 5.6], [6.5, 6.2, 6.3]]],
        ['general:прыжок в длину с места', 'Прыжок в длину с места', 'general', 'см.', 'higher', [
            [190, 198, 205], [185, 190, 188], [200, 205, 210], [180, 186, 195],
            [165, 170, 176], [160, 163, 170], [170, 168, 175], [155, 160, 162]]],
        ['special:подъём ног', 'Подъём ног', 'special', 'кол-во.повт.', 'higher', [
            [8, 10, 12], [9, 9, 11], [10, 11, 13], [7, 9, 10],
            [6, 8, 9], [5, 7, 8], [8, 9, 9], [null, 6, 8]]],
        ['special:мостик', 'Мостик', 'special', 'сек.', 'higher', [
            [25, 28, 30], [22, 26, 27], [28, 30, 33], [20, 22, 25],
            [18, 21, 22], [15, 18, 20], [20, 20, 24], [16, 19, 21]]],
    ]
    const tests = defs.map(([key, name, type, unit, dir, scores]) => ({
        key, name, type, unit, better_direction: dir,
        rows: athletes.map((fio, i) => ({
            athlete_id: i + 1,
            name: fio,
            values: Object.fromEntries(periods.map((p, k) => {
                const score = scores[i][k]
                return [String(p.id), score === null
                    ? {score: null, result: 'absent'}
                    : {score, result: 'passed'}]
            })),
        })),
    }))
    return {periods, tests}
})()
