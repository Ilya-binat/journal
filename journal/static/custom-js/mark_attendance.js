function showToast({type = 'success', title, message, duration = 4000}) {
    const container = document.getElementById('att-toast-container');
    const icons = {
        success: 'bi bi-check-circle-fill',
        error: 'bi bi-x-circle-fill',
        warning: 'bi bi-exclamation-circle-fill'
    };
    const toast = document.createElement('div');
    toast.className = `att-toast ${type}`;
    toast.style.position = 'relative';
    toast.innerHTML = `
            <div class="att-toast-icon ${type}"><i class="${icons[type]}"></i></div>
            <div class="att-toast-body">
                <p class="att-toast-title">${title}</p>
                ${message ? `<p class="att-toast-msg">${message}</p>` : ''}
            </div>
            <button class="att-toast-close" aria-label="Закрыть"><i class="bi bi-x"></i></button>
            <div class="att-toast-progress" style="width:100%"></div>
        `;
    container.appendChild(toast);
    requestAnimationFrame(() => requestAnimationFrame(() => toast.classList.add('show')));

    const progress = toast.querySelector('.att-toast-progress');
    progress.style.transition = `width ${duration}ms linear`;
    requestAnimationFrame(() => requestAnimationFrame(() => {
        progress.style.width = '0%';
    }));

    const dismiss = () => {
        toast.classList.remove('show');
        toast.classList.add('hide');
        setTimeout(() => toast.remove(), 400);
    };
    toast.querySelector('.att-toast-close').addEventListener('click', dismiss);
    const timer = setTimeout(dismiss, duration);
    toast.addEventListener('mouseenter', () => clearTimeout(timer));
    toast.addEventListener('mouseleave', () => setTimeout(dismiss, 1500));
}

const slotData = window.slotData;
const totalStudents = document.querySelectorAll('.att-row').length;

let allPresentActive = false;
let allAbsentActive = false;

function updateStats() {
    const present = document.querySelectorAll('input[data-action="present"]:checked').length;
    const absent = document.querySelectorAll('input[data-action="absent"]:checked').length;
    const excused = document.querySelectorAll('input[data-action="excused"]:checked').length;
    const marked = present + absent + excused;

    document.getElementById('cnt-present').textContent = present;
    document.getElementById('cnt-absent').textContent = absent;
    document.getElementById('cnt-excused').textContent = excused;
    document.getElementById('att-prog-label').textContent = `${marked} из ${totalStudents} отмечено`;
    document.getElementById('att-prog-fill').style.width = totalStudents
        ? Math.round(marked / totalStudents * 100) + '%'
        : '0%';
}

function collectData() {
    const result = [];
    document.querySelectorAll('.att-row').forEach(row => {
        const checked = row.querySelector('input.att-radio:checked');
        const textarea = row.querySelector('textarea.att-textarea');
        if (checked) {
            result.push({
                student_id: checked.dataset.id,
                status: checked.dataset.action,
                comment: textarea ? textarea.value : ''
            });
        }
    });
    return result;
}

// Чипы: установка / снятие отметки
document.querySelectorAll('.att-chip-label').forEach(label => {
    label.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        allPresentActive = false;
        allAbsentActive = false;

        const radio = this.querySelector('input.att-radio');
        const wasChecked = radio.checked;

        // Сбрасываем всю группу вручную
        document.querySelectorAll(`input[name="${radio.name}"]`).forEach(r => r.checked = false);

        if (!wasChecked) radio.checked = true;

        updateStats();
    });
});

// Открытие / закрытие комментария
document.querySelectorAll('.att-comment-toggle').forEach(btn => {
    btn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        const target = document.getElementById(this.dataset.target);
        if (target) target.classList.toggle('open');
    });
});
//  Закрытие блока комментариев
document.querySelectorAll('.save-comment-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        const target = document.getElementById(this.dataset.target);
        if (target) target.classList.toggle('open');
    });
});

// Все присутствуют (повторный клик — сброс)
document.getElementById('all-present').addEventListener('click', () => {
    if (allPresentActive) {
        document.querySelectorAll('input[data-action="present"]').forEach(r => r.checked = false);
        allPresentActive = false;
    } else {
        document.querySelectorAll('input[data-action="present"]').forEach(r => r.checked = true);
        document.querySelectorAll('input[data-action="absent"]').forEach(r => r.checked = false);
        document.querySelectorAll('input[data-action="excused"]').forEach(r => r.checked = false);
        allPresentActive = true;
        allAbsentActive = false;
    }
    updateStats();
});

// Все отсутствуют (повторный клик — сброс)
document.getElementById('all-absent').addEventListener('click', () => {
    if (allAbsentActive) {
        document.querySelectorAll('input[data-action="absent"]').forEach(r => r.checked = false);
        allAbsentActive = false;
    } else {
        document.querySelectorAll('input[data-action="absent"]').forEach(r => r.checked = true);
        document.querySelectorAll('input[data-action="present"]').forEach(r => r.checked = false);
        document.querySelectorAll('input[data-action="excused"]').forEach(r => r.checked = false);
        allAbsentActive = true;
        allPresentActive = false;
    }
    updateStats();
});

// Поиск
document.getElementById('att-search').addEventListener('input', function () {
    const q = this.value.toLowerCase();
    document.querySelectorAll('.att-row').forEach(row => {
        row.style.display = row.dataset.name.includes(q) ? '' : 'none';
    });
});

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

// Сохранение информации о посещении
const saveAttendance = document.querySelector('.save-attendance-btn');
saveAttendance.addEventListener('click', async () => {
    const checkedStudents = document.querySelectorAll('.att-radio:checked');

    if (checkedStudents.length === 0) {
        showToast({
            type: 'warning',
            title: 'Нет отмеченных',
            message: 'Отметьте хотя бы одного спортсмена перед сохранением.'
        });
        return;
    }

    const unmarked = totalStudents - checkedStudents.length;
    const saveBtn = document.getElementById('save-btn');
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i> Сохранение...';

    const now = new Date();
    const arrivalTime = now.toTimeString().slice(0, 8);
    const payload = [...checkedStudents].map(input => ({
        student_id: input.dataset.id,
        status: input.dataset.action,
        note: input.closest('.att-row').querySelector('.att-textarea').value,
        arrival_time: arrivalTime
    }));

    try {
        const response = await fetch(`/teacher/save_attendance/${slotData.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const msg = unmarked > 0
                ? `Сохранено ${checkedStudents.length} чел. · ${unmarked} не отмечено`
                : `Все ${checkedStudents.length} спортсменов отмечены`;
            showToast({type: 'success', title: 'Посещаемость сохранена', message: msg});
        } else {
            showToast({
                type: 'error',
                title: 'Ошибка сохранения',
                message: 'Сервер вернул ошибку. Попробуйте ещё раз.'
            });
        }
    } catch (err) {
        showToast({
            type: 'error',
            title: 'Ошибка',
            message: 'Нет соединения с сервером. Проверьте сеть.'
        });
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="bi bi-check2 me-1"></i> Сохранить';
    }
});

//Предзаполнение данных
let attendance = slotData.attendance
document.querySelectorAll('.att-row').forEach(
    (row) => {
        let radio = row.querySelector('input.att-radio')
        if (!radio) return

        let studentId = radio.dataset.id
        let saved = attendance[studentId]
        if (!saved) return

        const target = row.querySelector(`input[data-action="${saved.status}"]`)
        if (target) target.checked = true
        if (saved.note) {
            let textarea = row.querySelector('.att-textarea')
            if (textarea) textarea.value = saved.note
        }
    }
)
updateStats()

