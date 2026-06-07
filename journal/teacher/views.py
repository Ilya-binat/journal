from django.shortcuts import render, get_object_or_404, redirect
from .utils import *
from administrator.models import *
from datetime import datetime, date, timedelta
import json
from django.utils import timezone
from users.decorators import role_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse


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
    group_name = slot.group.group_name
    start_time = slot.start_time
    end_time = slot.end_time
    slot_date = slot.date
    hall = slot.hall.hall_name
    group_members = [member.student for member in slot.group.group_students.all()]
    slot_data = json.dumps({
        'id': slot.id,
        'date': str(slot.date),
        'start_time': str(slot.start_time),
        'end_time': str(slot.end_time),
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


@role_required('Тренер')
def mark_student(request, slot_id, student_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        status = data.get('status')
        note = data.get('note')
        arrival_time = data.get('arrival_time')
        Attendance.objects.create(
            slot_id=slot_id,
            student_id=student_id,
            note=note,
            status=status,
            marked_by=request.user,
            arrival_time=arrival_time
        )

        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})
