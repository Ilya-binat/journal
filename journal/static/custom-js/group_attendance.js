const MONTHS = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
const DAYS_SHORT = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
const TRAINING_DAYS = [1, 3, 5]; // Mon, Wed, Fri

const STUDENTS = [
    {name: 'Иван Иванов', init: 'ИИ'},
    {name: 'Пётр Петров', init: 'ПП'},
    {name: 'Сергей Сидоров', init: 'СС'},
    {name: 'Андрей Кузнецов', init: 'АК'},
    {name: 'Дмитрий Морозов', init: 'ДМ'},
    {name: 'Алексей Волков', init: 'АВ'},
    {name: 'Никита Борисов', init: 'НБ'},
    {name: 'Максим Швецов', init: 'МШ'},
    {name: 'Владимир Комаров', init: 'ВК'},
    {name: 'Егор Васильев', init: 'ЕВ'},
];

let cur = new Date(2026, 5, 1);

function seed(s) {
    let h = 0;
    for (let i = 0; i < s.length; i++) h = Math.imul(31, h) + s.charCodeAt(i) | 0;
    return Math.abs(h)
}

function rand(s) {
    let x = seed(s);
    return () => {
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        return (x >>> 0) / 4294967296
    }
}

function statusFor(student, day, month, year) {
    const r = rand(student + day + month * 31 + year * 365);
    const v = r();
    if (v < 0.72) return 'present';
    if (v < 0.88) return 'absent';
    return 'excused';
}

function render() {
    const y = cur.getFullYear(), m = cur.getMonth();
    document.getElementById('monthLabel').textContent = MONTHS[m] + ' ' + y;

    const daysInMonth = new Date(y, m + 1, 0).getDate();
    const today = new Date();

    const days = [];
    for (let d = 1; d <= daysInMonth; d++) {
        const date = new Date(y, m, d);
        const dow = date.getDay();
        const isTraining = TRAINING_DAYS.includes(dow);
        days.push({d, dow, isTraining});
    }
    const trainingDays = days.filter(x => x.isTraining);

    /* HEAD */
    const thead = document.getElementById('tHead');
    let htr = '<tr><th class="name-col">Спортсмены</th>';
    for (const {d, dow, isTraining} of days) {
        const isToday = (today.getFullYear() === y && today.getMonth() === m && today.getDate() === d);
        const cls = isToday ? 'day-hd today' : 'day-hd';
        htr += `<th class="day-col"><div class="${cls}"><span class="dn">${DAYS_SHORT[dow]}</span><span class="dd">${d}</span></div></th>`;
    }
    htr += '</tr>';
    thead.innerHTML = htr;

    /* BODY */
    let totalP = 0, totalA = 0, totalE = 0;
    const tbody = document.getElementById('tBody');
    let rows = '';
    STUDENTS.forEach((st, si) => {
        rows += `<tr><td class="name-cell"><div class="name-cell-inner"><div class="av c${si % 10}">${st.init}</div><span class="sn">${st.name}</span></div></td>`;
        for (const {d, isTraining} of days) {
            if (!isTraining) {
                rows += `<td><i class="bi bi-circle-fill dot none" title="Тренировки не было"></i></td>`;
            } else {
                const s = statusFor(st.name, d, m, y);
                const icon = s === 'present' ? 'check-circle-fill' : s === 'absent' ? 'x-circle-fill' : 'exclamation-circle-fill';
                const title = s === 'present' ? 'Был' : s === 'absent' ? 'Отсутствовал' : 'По справке';
                rows += `<td><i class="bi bi-${icon} dot ${s}" title="${title}"></i></td>`;
                if (s === 'present') totalP++;
                else if (s === 'absent') totalA++;
                else totalE++;
            }
        }
        rows += '</tr>';
    });
    tbody.innerHTML = rows;

    const total = totalP + totalA + totalE;
    const pct = n => total ? Math.round(n / total * 100) + '%' : '0%';
    document.getElementById('s-present').textContent = totalP.toLocaleString();
    document.getElementById('s-absent').textContent = totalA.toLocaleString();
    document.getElementById('s-excused').textContent = totalE.toLocaleString();
    document.getElementById('s-total').textContent = trainingDays.length;
    document.getElementById('s-present-pct').textContent = pct(totalP);
    document.getElementById('s-absent-pct').textContent = pct(totalA);
    document.getElementById('s-excused-pct').textContent = pct(totalE);
    document.getElementById('s-total-sub').textContent = STUDENTS.length + ' спортсменов';
}

document.getElementById('prevM').addEventListener('click', () => {
    cur = new Date(cur.getFullYear(), cur.getMonth() - 1, 1);
    render()
});
document.getElementById('nextM').addEventListener('click', () => {
    cur = new Date(cur.getFullYear(), cur.getMonth() + 1, 1);
    render()
});

document.querySelectorAll('.period-tab').forEach(btn => {
    btn.addEventListener('click', function () {
        document.querySelectorAll('.period-tab').forEach(b => b.classList.remove('on'));
        this.classList.add('on');
    });
});

render();