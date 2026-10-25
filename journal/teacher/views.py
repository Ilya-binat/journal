from io import BytesIO
from urllib.parse import quote

from django.shortcuts import render, get_object_or_404, redirect
from openpyxl.styles import Side, Border, Alignment, Font
from openpyxl.utils import get_column_letter

from .utils import *
from administrator.models import *
from datetime import datetime, date, timedelta
import json
from django.utils import timezone
from users.decorators import role_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from collections import defaultdict
from users.models import *
from openpyxl import Workbook


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


# закончил тут
@role_required('Тренер')
def attendance_report(request):
    """Главная страница — только рендер шаблона"""
    groups = Group.objects.filter(coach=request.user)
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
            .select_related('student', 'slot')  # Догружаем дополгительную связанную информацию
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
        {'id': s.id, 'date': s.date.strftime('%Y-%m-%d'), 'dow': s.date.weekday()}
        for s in slots
    ]
    # Формируем тело таблицы посещения
    rows = []
    for student_id, info in student_map.items():
        statuses = []
        for s in slots:
            statuses.append(status_grid[student_id].get(s.id, 'None'))
        rows.append({'student': info, 'statuses': statuses})

    return JsonResponse({
        'slots': slots_data,
        'rows': rows,
        'stats': {
            'present': present_count, 'present_pct': percent(present_count, total),
            'absent': absent_count, 'absent_pct': percent(absent_count, total),
            'excused': excused_count, 'excused_pct': percent(excused_count, total),
            'training_days': len(slots_id),
            'students': len(student_map),
        }
    })


# Функция для КПИ
@role_required('Тренер')
def exams(request):
    groups = Group.objects.filter(coach=request.user)

    current_year = date.today().year
    years = [
        current_year,
        current_year - 1,
        current_year - 2,
        current_year - 3,
        current_year - 4
    ]

    return render(request, 'exams.html', {'groups': groups,
                                          'years': years,
                                          'selected_year': current_year
                                          })


def build_exams_data(group):
    data = StudentGroup.objects.filter(group=group)
    students = CustomUser.objects.filter(
        pk__in=data.values('student')
    )

    # Сбор статистики по группе
    assessment = Assessment.objects.filter(group=group).order_by('-date_start', '-id').first()
    if assessment is None:
        return {
            'students_count': students.count(),
            'passed': 0,
            'absent': 0,
            'failed': 0,
            'passed_percent': 0,
            'absent_percent': 0,
            'failed_percent': 0,
            'avg_percent': 0,
            'thead': [],
            'table': {},
            'assessment': None,
        }

    test_items = list(TestItem.objects.filter(sport_type=assessment.sport_type, stage=assessment.next_stage).order_by(
        "assessment_type", "id"))
    thead = [{'id': test_item.id, 'name': test_item.name, 'unit': test_item.unit,
              'assessment_type': test_item.assessment_type} for test_item in test_items]

    assessment_result = AssessmentResult.objects.filter(assessment=assessment)
    total = students.count()
    total_test_items = len(test_items)  # Подсчет общего кол-ва испытаний
    results_by_athlete = defaultdict(dict)  # default_dict - дает возможность создать вложенный словарь
    athlete_names = {}

    for item in assessment_result:
        results_by_athlete[item.athlete_id][item.test_item_id] = item

    stats_dict = {
        'passed': 0,
        'failed': 0,
        'absent': 0
    }
    # Подсчет процента сдавших и не сдавших

    table = {}
    # Переменные для подсчета среднего процента по группе
    total_percent_sum = 0
    total_percent_count = 0

    for student in students.order_by('last_name', 'first_name'):
        athlete_id = student.id
        results_by_item = results_by_athlete.get(athlete_id, {})
        statuses = [r.result for r in results_by_item.values()]
        countable = [i for i in statuses if i in ('failed', 'passed')]
        items = total_test_items - statuses.count('exempted')
        total_percent = (
            round(statuses.count('passed') / items * 100)
            if items > 0 and countable
            else None
        )
        if total_percent is not None and total_percent >= KPI_PASS_PERCENT:
            status = "passed"
        elif "failed" in statuses:
            status = "failed"
        elif "absent" in statuses:
            status = "absent"
        else:
            status = None

        if status:
            stats_dict[status] += 1

        if total_percent is not None:
            total_percent_sum += total_percent
            total_percent_count += 1

        tests = []
        for item in test_items:
            result_row = results_by_item.get(item.id)
            if result_row is None:
                tests.append({
                    'name': item.name,
                    'score': '-',
                    'result': 'empty'
                })
            else:
                tests.append({
                    'name': item.name,
                    'score': result_row.score if result_row.score is not None else '-',
                    'result': result_row.result
                })
        table[athlete_id] = {
            'athlete': student.get_full_name(),
            'total_percent': total_percent,
            'tests': tests,
            'status': status
        }

    percents = {
        f'{key}_percent': round(value / total * 100) if total else 0
        for key, value in stats_dict.items()
    }
    avg_percent = (
        round(total_percent_sum / total_percent_count)
        if total_percent_count else 0
    )

    return {
        'students_count': total,
        **stats_dict,
        **percents,
        'avg_percent': avg_percent,
        'pass_percent': KPI_PASS_PERCENT,
        'table': table,
        'thead': thead,
        'assessment': {
            'name': assessment.name,
            'group': str(assessment.group),
            'next_stage': assessment.next_stage,
            'date_start': assessment.date_start.strftime('%d.%m.%Y'),
            'date_end': assessment.date_end.strftime('%d.%m.%Y'),
            'year': assessment.date_start.year,
            'group_stage': assessment.group.stage,
            'coach': assessment.coach.get_short_name(),
        }
    }


# Функция для вывода кол-ва спортсменов и самих спортсменов
@role_required('Тренер')
def fetch_exams_data(request):
    group = request.GET.get('group')
    return JsonResponse(build_exams_data(group))


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


# Добавление результатов экзамена
@role_required('Тренер')
def add_exam_result(request):
    data = json.loads(request.body)  # json строку переводим в python объект
    # берем id экзамена
    assessment_id = data.get('assessment_id')
    # берем id упражнение
    test_item_id = data.get('test_item_id')
    # id спортсмена
    athlete_id = data.get('athlete_id')
    # проставление результата
    action = data.get('action')

    # Находим упражнение
    test_item = get_object_or_404(TestItem, pk=test_item_id)
    # Находим спортсмена
    athlete = get_object_or_404(CustomUser, pk=athlete_id)

    # Создаем условие при котором заполняем результат экзамена
    if action == 'absent':
        result, score = 'absent', None
    elif action == 'exempted':
        result, score = 'exempted', None
    else:
        try:
            score = float(data.get('score'))
        except(TypeError, ValueError):
            return JsonResponse({
                'success': False,
                'error': 'Не корректоное значение результата',
            }, status=400)

        if test_item.min_value is not None and score < test_item.min_value:
            return JsonResponse({
                'success': False,
                'error': f'Результат не может быть меньше {test_item.min_value}'
            }, status=400)

        if test_item.max_value is not None and score > test_item.max_value:
            return JsonResponse({
                'success': False,
                'error': f'Результат не может быть боьше {test_item.min_value}'
            }, status=400)

        passed = is_score_passed(test_item, athlete, score)
        result = 'passed' if passed else 'failed'

    # Находим результат спортсмена по экзамену и упражнению и вносим результат
    updated = AssessmentResult.objects.filter(
        assessment_id=assessment_id,
        test_item_id=test_item_id,
        athlete_id=athlete_id
    ).update(score=score, result=result)

    if not updated:
        return JsonResponse({
            'success': False,
            'error': 'Результат не найден',
        }, status=404)
    return JsonResponse({
        'success': True,
        'score': score,
        'result': result
    }, status=200)


# Функция для получения данных станции
# станция это модальное окно для заполнения результатов экзамена
@role_required('Тренер')
def fetch_station_data(request):
    # Достаем группу
    group_id = request.GET.get('group')
    # Берем испытания для группы сортирую подню начала в порядке убывания(от сегодня назад)
    assessment = Assessment.objects.filter(group=group_id).order_by('-date_start', '-id').first()

    # Если испытание не найдено возвращаем пустые данные
    if not assessment:
        return JsonResponse({
            'assessment_id': None,
            'test_items': [],
            'selected_test_item': None,
            'queue': []
        })
    # Список испытвний в экзамене(ищем через вид спрорта и этап подготовки)
    test_items = list(TestItem.objects.filter(
        sport_type=assessment.sport_type,
        stage=assessment.next_stage
    ).order_by('assessment_type', 'id'))

    test_item = request.GET.get('test_item')

    # Если выбрано конкретное испытание то возвращвем его
    if test_item:
        selected = get_object_or_404(TestItem, pk=test_item)
    # Если не выбрано выбираем первое испытние в котор не заполнены рез-ты
    else:
        selected = next(
            (i for i in test_items if AssessmentResult.objects.filter(
                assessment=assessment, test_item=i, result='empty'
            ).exists()),
            test_items[0]
            if test_items else None
        )
    items_data = []

    for item in test_items:
        qs = AssessmentResult.objects.filter(assessment=assessment, test_item=item)
        items_data.append({
            'id': item.id,
            'name': item.name,
            'unit': item.get_unit_display(),
            'assessment_type': item.assessment_type,
            'min_value': item.min_value,
            'max_value': item.max_value,
            'done': qs.exclude(result='empty').count(),
            'total': qs.count()
        })

    queue = []

    if selected:
        results = (
            AssessmentResult.objects.filter(assessment=assessment, test_item=selected)
                .select_related('athlete')  # select это загрузка связанных данных - информации о спортсмене
                .order_by('athlete__last_name', 'athlete__first_name')
        )
        queue = [{
            'athlete_id': i.athlete_id,
            'name': i.athlete.get_full_name(),
            'result': i.result,
            'score': i.score
        } for i in results]

    return JsonResponse({
        'assessment_id': assessment.id,
        'test_items': items_data,
        'selected_test_item': selected.id if selected else None,
        'selected_unit': selected.get_unit_display() if selected else '',
        'queue': queue
    })


@role_required('Тренер')
def fetch_athlete_dynamics(request):
    """История спортсмена и рейтинг текущего состава его группы по каждому КПИ."""
    from math import isfinite

    try:
        group_id = int(request.GET.get('group', ''))
        athlete_id = int(request.GET.get('athlete', ''))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Некорректная группа или спортсмен'}, status=400)

    group = get_object_or_404(Group, pk=group_id, coach=request.user)
    students = list(CustomUser.objects.filter(
        pk__in=StudentGroup.objects.filter(group=group).values('student')
    ).order_by('last_name', 'first_name', 'id'))
    athlete = next((student for student in students if student.id == athlete_id), None)
    if athlete is None:
        return JsonResponse({'success': False, 'error': 'Спортсмен не состоит в этой группе'}, status=404)

    assessments = list(Assessment.objects.filter(group=group).order_by('date_start', 'id'))
    period_index = {assessment.id: i for i, assessment in enumerate(assessments)}
    # Каталог нужен и для испытаний, по которым ещё нет ни одной записи.
    items = list(TestItem.objects.filter(
        sport_type_id__in={assessment.sport_type_id for assessment in assessments},
        stage__in={assessment.next_stage for assessment in assessments},
    ).order_by('assessment_type', 'id'))
    programs = {
        assessment.id: {item.id for item in items
                        if item.sport_type_id == assessment.sport_type_id
                        and item.stage == assessment.next_stage}
        for assessment in assessments
    }
    results = list(AssessmentResult.objects.filter(
        assessment__in=assessments, athlete_id__in=[student.id for student in students]
    ).select_related('test_item').order_by('id'))
    items_by_id = {item.id: item for item in items}
    for result in results:
        items_by_id[result.test_item_id] = result.test_item
        programs[result.assessment_id].add(result.test_item_id)

    def finite(value):
        return value if value is not None and isfinite(value) else None

    tests = {}
    for item in items_by_id.values():
        norm = (item.max_cor_male if athlete.gender == 'Мужчина' else
                item.max_cor_female if athlete.gender == 'Женщина' else None)
        tests[item.id] = {
            'id': item.id, 'name': item.name, 'unit': item.get_unit_display(),
            'assessment_type': item.assessment_type,
            'norm': finite(norm), 'norm_male': finite(item.max_cor_male),
            'norm_female': finite(item.max_cor_female),
            'better_direction': item.better_direction,
            'values': [None] * len(assessments),
            'rankings': [[] for _ in assessments],
        }
    # При дубликатах используем последнюю запись, не считаем одного участника дважды.
    unique_results = {(r.assessment_id, r.athlete_id, r.test_item_id): r for r in results}
    names = {student.id: student.get_full_name() for student in students}
    totals = {a.id: {s.id: {'passed': 0, 'filled': 0} for s in students} for a in assessments}
    for result in unique_results.values():
        index = period_index[result.assessment_id]
        test = tests[result.test_item_id]
        score = finite(result.score)
        if result.athlete_id == athlete_id:
            test['values'][index] = {'score': score, 'result': result.result}
        total = totals[result.assessment_id][result.athlete_id]
        if result.result == 'passed':
            total['passed'] += 1
        if score is not None and result.result in ('passed', 'failed'):
            total['filled'] += 1
            test['rankings'][index].append({
                'athlete_id': result.athlete_id, 'name': names[result.athlete_id], 'score': score,
            })

    for test in tests.values():
        for ranking in test['rankings']:
            ranking.sort(key=lambda row: row['score'], reverse=test['better_direction'] != 'lower')
            previous_score, rank = None, 0
            for position, row in enumerate(ranking, 1):
                if row['score'] != previous_score:
                    rank = position
                row['rank'] = rank
                previous_score = row['score']

    periods = []
    for assessment in assessments:
        total = totals[assessment.id][athlete_id]
        eligible = [row for row in totals[assessment.id].values() if row['filled']]
        rank = (1 + sum(row['passed'] > total['passed'] for row in eligible)) if total['filled'] else None
        periods.append({
            'id': assessment.id, 'label': assessment.date_start.strftime('%d.%m.%Y'),
            'name': assessment.name, 'date_start': assessment.date_start.isoformat(),
            'future': assessment.date_start > timezone.localdate(),
            'invalid_dates': assessment.date_end < assessment.date_start,
            'test_ids': sorted(programs[assessment.id]),
            'summary': {**total, 'total': len(programs[assessment.id]), 'rank': rank,
                        'participants': len(eligible),
                        'ties': sum(row['passed'] == total['passed'] for row in eligible) if rank else 0},
        })
    return JsonResponse({
        'success': True, 'periods': periods,
        'tests': sorted(tests.values(), key=lambda test: (test['assessment_type'], test['id'])),
        'athlete_id': athlete_id, 'students_count': len(students),
    })


# Функция экспорта результатов КПИ в Excel
@role_required('Тренер')
def export_exams_excel(request):
    # Достаем id группы
    group = request.GET.get('group')

    # Если не передано id возвращаем ошибку
    if not group:
        return JsonResponse({
            'success': False,
            'error': 'Не передана группа'
        }, status=400)

    # Достаем всю необходимую информацию через группу
    # Экзамен, список и кол-во студентов, список упражнений,статистику
    data = build_exams_data(group)
    thead = data['thead']
    info = data['assessment']

    # Если у выбранной группы не назначен никакой экзамен, то выдаем ошибку
    if not info:
        return JsonResponse({
            'success': False,
            'error': 'Для этой группы нет КПИ'
        }, status=400)

    # Настраиваем шрифт,границы, выравнивание текста
    font = 'Times New Roman'
    thin = Side(style='thin', color='000000')
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    center = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # Настраиваем раскладку колонок(первым идет нумерация, ФИО, этап подготовки)
    # Начиная с 4-ой колонки идет первое испытание и вычисляется номер стобца последнего испытания
    # Так же вычисляется уровень спортивной квалификации и итог
    first_test_col = 4
    last_test_col = first_test_col + len(thead) - 1
    qual_col = last_test_col + 1
    total_col = last_test_col + 2
    last_col = total_col

    # Инициализация excel таблицы
    # Создание листа
    workbook = Workbook()
    ws = workbook.active
    workbook.title = "КПИ"

    # В первой строке пишим зоголовок
    ws.cell(
        1, 1,
        f"Контрольно-переводные нормативы по ОФП и СФП для перевода на следующий этап спортивной подготовки {info['year']}г."
    )
    # Соединяем столбцы так что бы поместился зоголовок
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    # Зодаем шрифт
    ws.cell(1, 1).font = Font(name=font, bold=True, size=12)
    # Выравниваем текст по центру() alignment-выравнивание
    ws.cell(1, 1).alignment = Alignment(horizontal='center', vertical='center')

    # Во 2, 3, 4 строчке указыываем тренера, группу и период
    ws.cell(2, 1, f"Тренер: {info['coach']}")
    ws.cell(3, 1, f"Группа: {info['group']}")
    ws.cell(4, 1, f"Период: {info['date_start']}-{info['date_end']}")

    for row in range(2, 5):
        ws.cell(row, 1).font = Font(name=font, bold=True, size=11)
        ws.merge_cells(start_row=row, end_row=row, start_column=1, end_column=2)

    # В 5-ой 6-ой и 7-ой строчках будет распологаться шапка таблицы начиная с 8-ой строки будет идти тело таблицы
    top = 5
    mid = 6
    sub = 7
    first_row = 8

    #  Вспомогательная функция которая всавляет текст в ячейку и дает нужные стили
    def head(rrow, col, value):
        column = ws.cell(rrow, col, value)
        column.font = Font(name=font, bold=True, size=10)
        column.alignment = center
        column.border = border

    # В первые 3 ячейки шапки таблицы вставляем текст и соединяем столбцы
    for c, title in ((1, '№'), (2, 'ФИО'), (3, 'Этап подготовки'),
                     (qual_col, 'Уровень спортивной квалификации'), (total_col, ' Итог')):
        head(top, c, title)
        ws.merge_cells(start_row=top, start_column=c, end_row=sub, end_column=c)

    # Блок для построения первого этажа нашей шапки таблицы.
    # Вставляем ОФП и СФП
    # А так же оъединяем подряд идущие колонки одного типа под общей ячейкой ОФП или СФП
    colmn = first_test_col
    while colmn <= last_test_col:
        kind = thead[colmn - first_test_col]['assessment_type']
        end = colmn
        while end + 1 <= last_test_col and thead[end + 1 - first_test_col]['assessment_type'] == kind:
            end += 1
        head(top, colmn, 'ОФП' if kind == 'general' else 'СФП')
        if end > colmn:
            ws.merge_cells(start_row=top, start_column=colmn, end_row=top, end_column=end)
        colmn = end + 1

    # Разновидности упражнения шпагат
    split_labels = [
        ('продольный', 'прод.'),
        ('поперечный', 'поп.'),
        ('правый', 'пр.'),
        ('левый', 'лев.'),
    ]

    # Вспомогательная функция для опредедления разновидности шпагата

    def split_info(name):
        low = name.strip().lower()

        if not low.startswith('шпагат'):
            return None, None

        for k, label in split_labels:
            if k in low:
                return 'шпагат', label
        return 'шпагат', name.strip()[6:].strip() or '-'

    colmn = first_test_col

    # После подготовки "первого этажа" таблицы делаем цикл по упражнениям. В зависимости от вида упражнения
    # Вставляем ячейку в СФП или в ОФП
    # Если упражнения не является шпагатов, то вставляем его в одну ячеку. Если упражнение шпагат, то сначал создаем
    # соединенную ячейку с текстом шпагат, и под ней вставляем все разновидности шпагатов.
    while colmn <= last_test_col:
        item = thead[colmn - first_test_col]
        group_name, label = split_info(item['name'])
        if group_name:
            end = colmn
            while end + 1 <= last_test_col and split_info(thead[end + 1 - first_test_col]['name'])[0] == group_name:
                end += 1
            head(mid, colmn, group_name)
            if end > colmn:
                ws.merge_cells(start_row=mid, start_column=colmn, end_row=mid, end_column=end)
            for i in range(colmn, end + 1):
                head(sub, i, split_info(thead[i - first_test_col]['name'])[1])
            colmn = end + 1
        else:
            unit = item.get('unit_display') or ''

            head(mid, colmn, f'{item["name"]} ({unit.strip(".")})' if unit else item['name'])
            head(sub, colmn, None)
            ws.merge_cells(start_row=mid, start_column=colmn, end_row=sub, end_column=colmn)
            colmn += 1

    # Вспомогательная функция для форматирования не целых чисел
    def format_score(score):
        if isinstance(score, float) and score.is_integer():
            score = int(score)
        return str(score).replace('.', ',')

    #  Функция для возвращающая вердикт в зависимости от результата в контексте одного упражнения
    def cell_text(test):
        result = test['result']
        if result == 'passed':
            return f"{format_score(test['score'])}/сдано"
        if result == 'failed':
            return f"{format_score(test['score'])}/не сдано"
        if result == 'absent':
            return 'отс.'
        if result == 'exempted':
            return 'осв.'
        return ""

    # Функция определяющая итог всего испытания
    def overall_text(row1):
        result_dict = {
            'passed': 'сдано',
            'failed': 'не сдано',
            'absent': 'не проходил'
        }
        return result_dict.get(row1['status'], '')

    # Блок для вставки тела таблицы
    row_num = first_row
    for index, row in enumerate(data['table'].values(), start=1):
        # Сначала вытаскиваем порядкой номе, ФИО, текущий этап подготовки
        values = [index, row['athlete'], info['group_stage']]
        # Вставляем результаты упражнений
        values += [cell_text(i) for i in row['tests']]
        # Вставляем следующий этап подготовки и итог
        values += [None, overall_text(row)]

        # Циклом проходимся по столбцам вставляем текст и стилизуем
        for c, value in enumerate(values, start=1):
            cell = ws.cell(row_num, c, value)
            cell.border = border
            cell.alignment = left if c == 2 else center
            cell.font = Font(
                name=font, size=10,
                color='C00000' if isinstance(value, str) and 'не сдано' in value else '000000'

            )
        row_num += 1

    # Настраиваем ширину столбцов
    ws.column_dimensions['A'].width = 5
    ws.column_dimensions['B'].width = 35
    ws.column_dimensions['C'].width = 15

    for i in range(first_test_col, last_test_col + 1):
        ws.column_dimensions[get_column_letter(i)].width = 15
    ws.column_dimensions[get_column_letter(qual_col)].width = 16
    ws.column_dimensions[get_column_letter(total_col)].width = 12
    ws.row_dimensions[mid].height = 75
    ws.freeze_panes = ws.cell(first_row, 3)
    ws.page_setup.orientation = 'landscape'
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    # Подготавливаемся к скачиванию
    buffer = BytesIO()
    workbook.save(buffer)
    filename = f'КПИ_{info["group"]}_{date.today():%Y-%m-%d}.xlsx'

    # Отдаем файл excel
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    )
    response['Content-Disposition'] = (
        f"attachment; filename*=UTF-8''{quote(filename, safe='')}"
    )

    return response


# Функция аналитики КПИ:по каждому испытанию-кто сдал, кто не ссдал, сколько не хватило до норматива
@role_required('Тренер')
def fetch_exams_analytics(request):
    group = request.GET.get('group')
    assessment = Assessment.objects.filter(group=group).order_by('-date_start')

    if assessment is None:
        return JsonResponse({
            "assessment": None,
            "tests": []
        })

    test_items = list(TestItem.objects.filter(
        sport_type=assessment.sport_type, stage=assessment.next_stage
    ).order_by("assessment_type", "id"))
    students = list(
        CustomUser.objects.filter(
            id__in=StudentGroup.objects.filter(group=group).values("student")).order_by("last_name", "first_name")
    )
    results = {
        (r.athlete_id, r.test_item_id): r for r in AssessmentResult.objects.filter(assessment=assessment)
    }

    tests = []

    for item in test_items:
        counts = {
            "passed": 0,
            "failed": 0,
            "absent": 0,
            "empty": 0,
            "exempted": 0
        }

        rows = []

        for student in students:
            res = results.get((student.id, item.id))
            result = res.result if res else "empty"
            score = res.score if res else None

            counts[result] = counts.get(result, 0) + 1
            genders = {
                "Мужчина": 'male',
                "Женщина": 'female'
            }
            gender = genders.get(student.gender)
            norm = (item.max_cor_male if gender == 'male' else item.max_core_female if gender == 'female' else None)

            gap = None

            if result == 'failed' and score is not None and norm is not None:
                gap = round(score - norm if item.better_direction == 'lower' else norm - score, 2)

                if gap < 0:
                    gap = None

            rows.append({
                "athlete_id": student.id,
                "name": student.get_full_name,
                "gender": gender,
                "result": result,
                "score": score,
                "norm": norm,
                "gap": gap,
            })

        tests.append({
            "id": item.id,
            "name": item.name,
            "type": item.assessment_type,
            "unit": item.get_unit_display(),
            "better_direction": item.get_better_direction,
            "counts": counts,
            "rows": rows,
        })

    return JsonResponse({
        "assessment": {
            "name": assessment.name,
            "date_start": assessment.date_start.strftime('%d.%m.%Y'),
            "date_end": assessment.date_end.strftime('%d.%m.%Y'),
        },
        "student_count": len(students),
        "tests": tests,
    })
