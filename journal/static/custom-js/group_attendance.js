const MONTHS       = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'];
const MONTHS_SHORT = ['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек'];
const DAYS_SHORT   = ['Вс','Пн','Вт','Ср','Чт','Пт','Сб'];

// ─── State ────────────────────────────────────────────────────────────────────
const today = new Date();
let mode = 'month';  // '1day' | 'week' | 'month' | 'period'

let state = {
    // month
    monthYear:  today.getFullYear(),
    monthMonth: today.getMonth(),
    // 1day
    dayDate: new Date(today),
    // week
    weekYear: today.getFullYear(),
    weekNum:  getISOWeek(today),
    // period
    periodFrom: null,
    periodTo:   null,
};

// ─── Helpers ──────────────────────────────────────────────────────────────────
function getISOWeek(date) {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

function getWeeksInYear(year) {
    return getISOWeek(new Date(year, 11, 28));
}

// Возвращает [startDate, endDate] для ISO-недели
function isoWeekRange(year, week) {
    const simple = new Date(year, 0, 1 + (week - 1) * 7);
    const dow = simple.getDay();
    const ISOweekStart = new Date(simple);
    if (dow <= 4) ISOweekStart.setDate(simple.getDate() - simple.getDay() + 1);
    else          ISOweekStart.setDate(simple.getDate() + 8 - simple.getDay());
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

// ─── Сборка параметров для запроса ───────────────────────────────────────────
function buildParams() {
    const group = document.getElementById('groupSel')?.value || '';
    const p = { group, period: mode };


    if (mode === 'month') {
        p.year  = state.monthYear;
        p.month = state.monthMonth + 1;   // JS 0-based → Django 1-based
    } else if (mode === '1day') {
        p.date_from = dateToYMD(state.dayDate);
    } else if (mode === 'week') {
        const [ws] = isoWeekRange(state.weekYear, state.weekNum);
        p.date_from = dateToYMD(ws);      // Django сам вычислит пн–вс
    } else if (mode === 'period') {
        if (state.periodFrom) p.date_from = dateToYMD(state.periodFrom);
        if (state.periodTo)   p.date_to   = dateToYMD(state.periodTo);
    }
    console.log(p)
    return p;
}

// ─── AJAX запрос на бэк ───────────────────────────────────────────────────────
async function renderTable() {
    setLoading(true);

    const params = buildParams();
    const qs = new URLSearchParams(params).toString();
    const url = `/teacher/attendance/data/?${qs}`;

    try {
        const res = await fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });

        if (!res.ok) {
            throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        applyData(data);
    } catch (err) {
        console.error('Ошибка загрузки данных:', err);
        showError();
    } finally {
        setLoading(false);
    }
}

// ─── Применение данных из ответа ─────────────────────────────────────────────
function applyData({ slots, rows, stats }) {
    renderHead(slots);
    renderBody(rows, slots);
    renderStats(stats);
}

function renderHead(slots) {
    const todayYMD = dateToYMD(today);

    // Определяем, нужно ли показывать метку месяца (период охватывает >1 месяца)
    const months = new Set(slots.map(s => s.date.slice(0, 7)));
    const showMonth = months.size > 1;

    let htr = '<tr><th class="name-col">Спортсмены</th>';
    for (const slot of slots) {
        const d   = new Date(slot.date + 'T00:00:00');   // локальная дата без смещения
        const dow = d.getDay();
        const isToday = slot.date === todayYMD;
        const cls = isToday ? 'day-hd today' : 'day-hd';
        const monthMark = showMonth
            ? `<span class="dm">${MONTHS_SHORT[d.getMonth()]}</span>`
            : '';
        htr += `<th class="day-col">
                  <div class="${cls}">
                    ${monthMark}
                    <span class="dn">${DAYS_SHORT[dow]}</span>
                    <span class="dd">${d.getDate()}</span>
                  </div>
                </th>`;
    }
    htr += '</tr>';
    document.getElementById('tHead').innerHTML = htr;
}

function renderBody(rows, slots) {
    const STATUS_ICON = {
        present: ['check-circle-fill',      'present', 'Был'],
        absent:  ['x-circle-fill',          'absent',  'Отсутствовал'],
        excused: ['exclamation-circle-fill', 'excused', 'По справке'],
        none:    ['circle-fill',             'none',    'Тренировки не было'],
    };

    if (!rows || rows.length === 0) {
        document.getElementById('tBody').innerHTML =
            `<tr><td colspan="100" style="text-align:center;padding:32px;color:#9CA3AF">Нет данных</td></tr>`;
        return;
    }

    let body = '';
    rows.forEach(({ student, statuses }, si) => {
        body += `<tr>
          <td class="name-cell">
            <div class="name-cell-inner">
              <div class="av c${si % 10}">${student.init}</div>
              <span class="sn">${student.name}</span>
            </div>
          </td>`;

        statuses.forEach(st => {
            const [icon, cls, title] = STATUS_ICON[st] ?? STATUS_ICON.none;
            body += `<td><i class="bi bi-${icon} dot ${cls}" title="${title}"></i></td>`;
        });

        body += '</tr>';
    });

    document.getElementById('tBody').innerHTML = body;
}

function renderStats({ present, present_pct, absent, absent_pct, excused, excused_pct, training_days, students }) {
    document.getElementById('s-present').textContent     = present.toLocaleString();
    document.getElementById('s-absent').textContent      = absent.toLocaleString();
    document.getElementById('s-excused').textContent     = excused.toLocaleString();
    document.getElementById('s-total').textContent       = training_days;
    document.getElementById('s-present-pct').textContent = present_pct + '%';
    document.getElementById('s-absent-pct').textContent  = absent_pct  + '%';
    document.getElementById('s-excused-pct').textContent = excused_pct + '%';
    document.getElementById('s-total-sub').textContent   = students + ' спортсменов';
}

// ─── UI: лоадер и ошибка ─────────────────────────────────────────────────────
function setLoading(on) {
    const tbody = document.getElementById('tBody');
    if (on) {
        tbody.innerHTML =
            `<tr><td colspan="100" style="text-align:center;padding:32px;color:#9CA3AF">
               <span class="spinner-border spinner-border-sm me-2" role="status"></span>Загрузка…
             </td></tr>`;
    }
}

function showError() {
    document.getElementById('tBody').innerHTML =
        `<tr><td colspan="100" style="text-align:center;padding:32px;color:#EF4444">
           <i class="bi bi-exclamation-triangle me-1"></i>Ошибка загрузки данных
         </td></tr>`;
}

// ─── Пикер периода ───────────────────────────────────────────────────────────
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
        area.innerHTML = `<input type="date" class="filter-select" id="dayPicker" value="${val}" style="min-width:160px">`;
        document.getElementById('dayPicker').addEventListener('change', function () {
            if (this.value) { state.dayDate = ymdToDate(this.value); renderTable(); }
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
        const toVal   = state.periodTo   ? dateToYMD(state.periodTo)   : '';
        area.innerHTML = `
          <div class="period-range">
            <div class="filter-group">
              <span class="filter-label">С</span>
              <input type="date" class="filter-select" id="periodFrom" value="${fromVal}" style="min-width:160px">
            </div>
            <div class="period-range-sep">—</div>
            <div class="filter-group">
              <span class="filter-label">По</span>
              <input type="date" class="filter-select" id="periodTo" value="${toVal}" style="min-width:160px">
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

// ─── Переключение режима (табы) ───────────────────────────────────────────────
const modeMap = { '1 день': '1day', 'Неделя': 'week', 'Месяц': 'month', 'Период': 'period' };

document.querySelectorAll('.period-tab').forEach(btn => {
    btn.addEventListener('click', function () {
        document.querySelectorAll('.period-tab').forEach(b => b.classList.remove('on'));
        this.classList.add('on');
        mode = modeMap[this.textContent.trim()] || 'month';
        renderPickerArea();
        renderTable();
    });
});

// Смена группы → перезагрузка
document.getElementById('groupSel')?.addEventListener('change', renderTable);

// ─── Init ─────────────────────────────────────────────────────────────────────
renderPickerArea();
renderTable();
