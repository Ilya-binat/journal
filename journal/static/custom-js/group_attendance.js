const MONTHS = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'];
const MONTHS_SHORT = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
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

// ─── State ────────────────────────────────────────────────────────────────────
const today = new Date();
let mode = 'month';  // '1day' | 'week' | 'month' | 'period'

let state = {
    // month
    monthYear: today.getFullYear(),
    monthMonth: today.getMonth(),
    // 1day
    dayDate: new Date(today),
    // week
    weekYear: today.getFullYear(),
    weekNum: getISOWeek(today),
    // period
    periodFrom: null,
    periodTo: null,
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function seed(s) {
    let h = 0;
    for (let i = 0; i < s.length; i++) h = Math.imul(31, h) + s.charCodeAt(i) | 0;
    return Math.abs(h);
}

function rand(s) {
    let x = seed(s);
    return () => {
        x ^= x << 13;
        x ^= x >> 17;
        x ^= x << 5;
        return (x >>> 0) / 4294967296;
    };
}

function statusFor(student, day, month, year) {
    const r = rand(student + day + month * 31 + year * 365);
    const v = r();
    if (v < 0.72) return 'present';
    if (v < 0.88) return 'absent';
    return 'excused';
}

function getISOWeek(date) {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

function getWeeksInYear(year) {
    const dec28 = new Date(year, 11, 28);
    return getISOWeek(dec28);
}

// Returns [startDate, endDate] for an ISO week
function isoWeekRange(year, week) {
    const simple = new Date(year, 0, 1 + (week - 1) * 7);
    const dow = simple.getDay();
    const ISOweekStart = new Date(simple);
    if (dow <= 4) ISOweekStart.setDate(simple.getDate() - simple.getDay() + 1);
    else ISOweekStart.setDate(simple.getDate() + 8 - simple.getDay());
    const ISOweekEnd = new Date(ISOweekStart);
    ISOweekEnd.setDate(ISOweekStart.getDate() + 6);
    return [ISOweekStart, ISOweekEnd];
}

function dateToYMD(d) {
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function ymdToDate(s) {
    const [y, m, d] = s.split('-').map(Number);
    return new Date(y, m - 1, d);
}

// Generate array of {d, dow, isTraining, date} for a date range [from, to]
function getDaysRange(from, to) {
    const days = [];
    const cur = new Date(from);
    while (cur <= to) {
        const dow = cur.getDay();
        days.push({
            d: cur.getDate(),
            dow,
            isTraining: TRAINING_DAYS.includes(dow),
            date: new Date(cur),
            month: cur.getMonth(),
            year: cur.getFullYear(),
        });
        cur.setDate(cur.getDate() + 1);
    }
    return days;
}

// ─── Period Picker UI ─────────────────────────────────────────────────────────
function renderPickerArea() {
    const area = document.getElementById('pickerArea');

    if (mode === 'month') {
        area.innerHTML = `
          <div class="month-nav">
            <button id="prevM" aria-label="Предыдущий месяц"><i class="bi bi-chevron-left"></i></button>
            <span id="monthLabel">${MONTHS[state.monthMonth]} ${state.monthYear}</span>
            <button id="nextM" aria-label="Следующий месяц"><i class="bi bi-chevron-right"></i></button>
          </div>`;
        document.getElementById('prevM').addEventListener('click', () => {
            if (state.monthMonth === 0) { state.monthYear--; state.monthMonth = 11; }
            else state.monthMonth--;
            renderPickerArea();
            renderTable();
        });
        document.getElementById('nextM').addEventListener('click', () => {
            if (state.monthMonth === 11) { state.monthYear++; state.monthMonth = 0; }
            else state.monthMonth++;
            renderPickerArea();
            renderTable();
        });

    } else if (mode === '1day') {
        const val = dateToYMD(state.dayDate);
        area.innerHTML = `<input type="date" class="filter-select" id="dayPicker" name="day" value="${val}" style="min-width:160px">`;
        document.getElementById('dayPicker').addEventListener('change', function () {
            if (this.value) {
                state.dayDate = ymdToDate(this.value);
                renderTable();
            }
        });

    } else if (mode === 'week') {
        const weeks = getWeeksInYear(state.weekYear);
        let options = '';
        for (let w = 1; w <= weeks; w++) {
            const [ws, we] = isoWeekRange(state.weekYear, w);
            const label = `Неделя ${w} (${ws.getDate()} ${MONTHS_SHORT[ws.getMonth()]} – ${we.getDate()} ${MONTHS_SHORT[we.getMonth()]})`;
            options += `<option value="${w}" ${w === state.weekNum ? 'selected' : ''}>${label}</option>`;
        }
        area.innerHTML = `
          <div class="week-picker">
            <div class="month-nav" style="min-width:auto;gap:4px">
              <button id="prevWY"><i class="bi bi-chevron-left"></i></button>
              <span id="weekYearLabel">${state.weekYear}</span>
              <button id="nextWY"><i class="bi bi-chevron-right"></i></button>
            </div>
            <select class="filter-select" id="weekSel" style="min-width:280px">${options}</select>
          </div>`;
        document.getElementById('prevWY').addEventListener('click', () => {
            state.weekYear--;
            const maxW = getWeeksInYear(state.weekYear);
            if (state.weekNum > maxW) state.weekNum = maxW;
            renderPickerArea();
            renderTable();
        });
        document.getElementById('nextWY').addEventListener('click', () => {
            state.weekYear++;
            const maxW = getWeeksInYear(state.weekYear);
            if (state.weekNum > maxW) state.weekNum = maxW;
            renderPickerArea();
            renderTable();
        });
        document.getElementById('weekSel').addEventListener('change', function () {
            state.weekNum = +this.value;
            renderTable();
        });

    } else if (mode === 'period') {
        const fromVal = state.periodFrom ? dateToYMD(state.periodFrom) : '';
        const toVal = state.periodTo ? dateToYMD(state.periodTo) : '';
        area.innerHTML = `
          <div class="period-range">
            <div class="filter-group">
              <span class="filter-label">С</span>
              <input type="date" class="filter-select" id="periodFrom" name="date_from" value="${fromVal}" style="min-width:160px">
            </div>
            <div class="period-range-sep">—</div>
            <div class="filter-group">
              <span class="filter-label">По</span>
              <input type="date" class="filter-select" id="periodTo" name="date_to" value="${toVal}" style="min-width:160px">
            </div>
          </div>`;
        document.getElementById('periodFrom').addEventListener('change', function () {
            state.periodFrom = this.value ? ymdToDate(this.value) : null;
            renderTable();
        });
        document.getElementById('periodTo').addEventListener('change', function () {
            state.periodTo = this.value ? ymdToDate(this.value) : null;
            renderTable();
        });
    }
}


// ─── Table Render ─────────────────────────────────────────────────────────────
function getActiveDays() {
    if (mode === 'month') {
        const from = new Date(state.monthYear, state.monthMonth, 1);
        const to = new Date(state.monthYear, state.monthMonth + 1, 0);
        return getDaysRange(from, to);
    } else if (mode === '1day') {
        return getDaysRange(state.dayDate, state.dayDate);
    } else if (mode === 'week') {
        const [from, to] = isoWeekRange(state.weekYear, state.weekNum);
        return getDaysRange(from, to);
    } else if (mode === 'period') {
        if (!state.periodFrom || !state.periodTo) return [];
        const from = state.periodFrom <= state.periodTo ? state.periodFrom : state.periodTo;
        const to = state.periodFrom <= state.periodTo ? state.periodTo : state.periodFrom;
        return getDaysRange(from, to);
    }
    return [];
}

function renderTable() {
    const days = getActiveDays();
    const trainingDays = days.filter(x => x.isTraining);

    /* HEAD */
    const thead = document.getElementById('tHead');
    let htr = '<tr><th class="name-col">Спортсмены</th>';
    for (const {d, dow, date} of days) {
        const isToday = dateToYMD(date) === dateToYMD(today);
        const cls = isToday ? 'day-hd today' : 'day-hd';
        // For multi-month range show month above date
        const showMonth = (mode === 'period' && days.some(x => x.month !== days[0].month));
        const monthMark = showMonth ? `<span class="dm">${MONTHS_SHORT[date.getMonth()]}</span>` : '';
        htr += `<th class="day-col"><div class="${cls}">${monthMark}<span class="dn">${DAYS_SHORT[dow]}</span><span class="dd">${d}</span></div></th>`;
    }
    htr += '</tr>';
    thead.innerHTML = htr;

    /* BODY */
    let totalP = 0, totalA = 0, totalE = 0;
    let rows = '';

    if (days.length === 0) {
        rows = `<tr><td colspan="100" style="text-align:center;padding:32px;color:#9CA3AF">Выберите период</td></tr>`;
    } else {
        STUDENTS.forEach((st, si) => {
            rows += `<tr><td class="name-cell"><div class="name-cell-inner"><div class="av c${si % 10}">${st.init}</div><span class="sn">${st.name}</span></div></td>`;
            for (const {d, date, isTraining} of days) {
                const m = date.getMonth(), y = date.getFullYear();
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
    }

    document.getElementById('tBody').innerHTML = rows;

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

// ─── Period Tab Switch ────────────────────────────────────────────────────────
const modeMap = {'1 день': '1day', 'Неделя': 'week', 'Месяц': 'month', 'Период': 'period'};

document.querySelectorAll('.period-tab').forEach(btn => {
    btn.addEventListener('click', function () {
        document.querySelectorAll('.period-tab').forEach(b => b.classList.remove('on'));
        this.classList.add('on');
        mode = modeMap[this.textContent.trim()] || 'month';
        renderPickerArea();
        renderTable();
    });
});

// ─── Init ─────────────────────────────────────────────────────────────────────
renderPickerArea();
renderTable();
