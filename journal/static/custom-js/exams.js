let groupSelect = document.querySelector('.group_select')

document.addEventListener('DOMContentLoaded', () => {
    fetchData()
})

groupSelect.addEventListener('change', () => {
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
    document.querySelector('.total_number').textContent = data.students_count;

    ['passed', 'failed', 'absent'].forEach(status => {
        document.querySelector(`.${status}_number`).textContent = data[status];
        document.querySelector(`.${status}_percent`).textContent = `${data[`${status}_percent`]}%`;
    });
    renderTableHead(data.thead)
    renderTableBody(data.thead, data.table)
    document.querySelector('.avg_number').textContent = `${data.avg_percent}%`
    document.querySelector('.avg_percent').querySelector('div').style.width=`${data.avg_percent}%`
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
            : row.total_percent >= 85 ? 'score-high' : 'score-mid'
        const scoreValue = row.total_percent === null ? '—' : row.total_percent

        tbody.insertAdjacentHTML('beforeend', `
            <tr>
                <td>${index}</td>
                <td class="athlete-cell"><span class="athlete-avatar-placeholder"><i class="bi bi-person-fill"></i></span>${row.athlete}</td>
                ${cells}
                <td class="kpi-score ${scoreClass}">${scoreValue ?? 'не добавлено'}</td>
            </tr>
        `)
    }
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
                    type:'warning',
                    title:'Не допустимое значение',
                    message:data.error || 'Проверьте введенный результат'
                })
                return
            }
            student.result = data.result
            student.score = data.score
            stationState.pending = stationState.queue.filter(s => s.result === 'empty')

            const item = stationState.testItems.find(t => t.id === stationState.selectedTestItemId)
            if (item) item.done += 1

            showToast({
                type:'success',
                title:'Результат сохранен'
            })

            renderStationPicker()
            renderStationProgress()
            renderStationActive()
            renderStationQueueList()
        })
        .catch(error => {
            console.error(error)
            showToast({
                type:'error',
                title: 'Ошибка',
                message:'Нет соединения с сервером, проверьте подключение'
            })
        })
}

// Функция отправки результата о освобождение или отсутствии
function submitQuickActions(action){
    const next = stationState.pending[0]

    if(!next) return
    submitStationResult(next, {action})
}

// Функция отправки резкльтата о сдачи или не сдачи
function submitScore(){
    const next = stationState.pending[0]

    if(!next) return
    const input = document.getElementById('stationScoreInput')
    const value = input.value.trim().replace(',', '.')

    if(value === '' || isNaN(Number(value))){
        input.focus()
        return
    }
    submitStationResult(next, {action:'score', score:Number(value)})

}

function showToast({ type = 'success', title, message, duration = 4000 }) {
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