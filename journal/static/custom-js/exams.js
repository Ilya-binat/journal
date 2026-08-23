let groupSelect = document.querySelector('.group_select')

document.addEventListener('DOMContentLoaded', ()=>{
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
    if (test.result  === 'empty') {
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