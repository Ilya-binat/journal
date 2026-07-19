from django.shortcuts import render, get_object_or_404, redirect
from .utils import *
from administrator.models import *
from datetime import datetime, date, timedelta
import json
from django.utils import timezone
from users.decorators import role_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from collections import defaultdict


@role_required('Тренер')
def teacher_schedule(request):
    # Получаем дату из URL
    date_str = request.GET.get('date')

    # Если дата есть -> используем её
    if date_str:
        current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        current_date = timezone.localdate()

    # Предыдущий и следующий день
    prev_week = current_date - timedelta(days=7)
    next_week = current_date + timedelta(days=7)

    # Слоты на выбранный день
    slots = Slot.objects.filter(
        date=current_date,
        coach=request.user
    )

    week_days = get_week_days(current_date)
    slots_count = slots.count()
    total_duration = count_training_time(request.user) or 0
    trainings = build_schedule_slots(slots) if slots.exists() else []
    week_trainings = get_week_training(request)

    return render(request, 'teacher_schedule.html', {
        'week_days': week_days,
        'slots': slots,
        'slots_count': slots_count,
        'current_date': current_date,
        'prev_week': prev_week,
        'next_week': next_week,
        'total_duration': total_duration,
        'trainings': trainings,
        'week_trainings': week_trainings,
    })


# Функция отметки студентов

def mark_attendance(request, slot_id):
    # Вывод слота со всей связанной информацией
    slot = get_object_or_404(Slot, pk=slot_id)
    group_members = [member.student for member in slot.group.group_students.all()]

    existing = Attendance.objects.filter(slot=slot)
    attendance_map = {
        a.student_id: {
            'status': a.status,
            'note': a.note
        }
        for a in existing

    }

    # Создание списка без использования гениратора словарей(a.)

    # attendance_map = {}
    # for a in existing:
    #     attendance_map [a.student_id] = {
    #         'status': a.status,
    #         'note': a.note
    #     }

    group_name = slot.group.group_name
    start_time = slot.start_time
    end_time = slot.end_time
    slot_date = slot.date
    hall = slot.hall.hall_name

    slot_data = json.dumps({
        'id': slot.id,
        'date': str(slot.date),
        'start_time': str(slot.start_time),
        'end_time': str(slot.end_time),
        'attendance': attendance_map
    })

    return render(request, 'mark_attendance.html', {
        'group_name': group_name,
        'start_time': start_time,
        'end_time': end_time,
        'slot_date': slot_date,
        'hall': hall,
        'group_members': group_members,
        'slot': slot_data,

    })


@require_POST
@role_required('Тренер')
def save_slot_notes(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id, coach=request.user)

    if request.method == "POST":
        # УДАЛЕНИЕ
        if "delete" in request.POST:
            slot.notes = ""
            slot.save()
            return redirect(request.META.get("HTTP_REFERER"))
        # СОХРАНЕНИЕ
        notes = request.POST.get("notes", "").strip()
        slot.notes = notes
        slot.save()

    return redirect(request.META.get("HTTP_REFERER"))


@require_POST
@role_required('Тренер')
def save_all_attendance(request, slot_id):
    data = json.loads(request.body)  # список [{student_id, status, note, arrival_time}]
    for item in data:
        Attendance.objects.update_or_create(
            slot_id=slot_id,
            student_id=item['student_id'],
            defaults={
                'status': item['status'],
                'note': item.get('note', ''),
                'arrival_time': item.get('arrival_time'),
                'marked_by': request.user,
            }
        )
    return JsonResponse({'status': 'success'})


@role_required('Тренер')
def attendance_report(request):
    """Главная страница — только рендер шаблона"""
    groups = Group.objects.all()
    return render(request, 'group_attendance.html', {'groups': groups})


@role_required('Тренер')
def attendance_report_data(request):
    # Подготовили переменные для фильтрации
    group_id = request.GET.get('group')
    period = request.GET.get('period', 'month')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    today = date.today()
    if period == 'day':
        d = _parse_date(date_from) or today
        from_date, to_date = d, d
    elif period == 'week':
        d = _parse_date(date_from) or today
        from_date = d - timedelta(days=d.weekday())
        to_date = from_date + timedelta(days=6)
    elif period == 'range':
        from_date = _parse_date(date_from) or today
        to_date = _parse_date(date_to) or today
        if from_date > to_date:
            from_date, to_date = to_date, from_date
    else:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        from_date = date(year, month, 1)
        to_date = (date(year, month + 1, 1) - timedelta(days=1)) \
            if month < 12 else date(year, 12, 31)

    # Вытащили слоты за выбранный период
    slots = Slot.objects.filter(date__range=(from_date, to_date))

    if group_id:
        slots = slots.filter(group_id=group_id)

    slots = slots.order_by('date')
    slots_id = list(slots.values_list('id', flat=True))
    attendances = (
        Attendance.objects
            .filter(slot_id__in=slots_id)
            .select_related('student', 'slot') # Догружаем дополгительную связанную информацию
            .order_by('student__last_name', 'student__first_name', 'slot__date')
    )

    # Формируем таблицу посещений в базе данных
    student_map = {}
    status_grid = defaultdict(dict)
    for attendance in attendances:
        student_id = attendance.student_id
        if student_id not in student_map:
            first_name = attendance.student.first_name or ''
            last_name = attendance.student.last_name or ''
            student_map[student_id] = {
                'id': student_id,
                'name': attendance.student.get_full_name(),
                'init': (first_name[:1] + last_name[:1]).upper()
            }
        status_grid[student_id][attendance.slot_id] = attendance.status

    # Формируем статистику посещения

    present_count = 0
    excused_count = 0
    absent_count = 0

    for attendance in attendances:
        if attendance.status == 'present':
            present_count += 1
        elif attendance.status == 'excused':
            excused_count += 1
        elif attendance.status == 'absent':
            absent_count += 1

    total = present_count + excused_count + absent_count

    slots_data = [
        {'id':s.id,'date':s.date.strftime('%Y-%m-%d'),'dow':s.date.weekday()}
        for s in slots
    ]
    # Формируем тело таблицы посещения
    rows = []
    for student_id, info in student_map.items():
        statuses = []
        for s in slots:
            statuses.append(status_grid[student_id].get(s.id, 'None'))
        rows.append({'student':info,'statuses':statuses})

    return JsonResponse({
        'slots': slots_data,
        'rows': rows,
        'stats': {
            'present': present_count, 'present_pct': percent(present_count,total),
            'absent': absent_count, 'absent_pct': percent(absent_count,total),
            'excused': excused_count, 'excused_pct': percent(excused_count,total),
            'training_days': len(slots_id),
            'students': len(student_map),
        }
    })


# Берет JS дату и преобразует ее в формат ГГГГ.ММ.ДД
def _parse_date(s):
    if not s:
        return None
    try:
        return date.fromisoformat(s)  # 'YYYY-MM-DD'
    except ValueError:
        return None


def percent(n, total):
    return round(n / total * 100) if total else 0
