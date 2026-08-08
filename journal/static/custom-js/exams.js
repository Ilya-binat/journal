let groupSelect = document.querySelector('.group_select')

groupSelect.addEventListener('change', () => {
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

})

function replaceData(data) {
    document.querySelector('.total_number').textContent = data.students_count;

    ['passed', 'failed', 'absent'].forEach(status => {
        document.querySelector(`.${status}_number`).textContent = data[status];
        document.querySelector(`.${status}_percent`).textContent = `${data[`${status}_percent`]}%`;
    });
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