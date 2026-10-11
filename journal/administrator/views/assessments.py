from ..models import *
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import *
from django.http import HttpResponse, JsonResponse
from users.decorators import role_required
from itertools import product
from django.views.decorators.http import require_POST


@role_required('Администратор')
def assessments(request):
    form = AssessmentForm()
    data = Assessment.objects.all()

    return render(request, "assessments.html", {"assessments": data, "form": form})

def stage_tests(next_stage, sport_type):
    # Испытания справочника для этапа и вида спорта КПИ
    return TestItem.objects.filter(stage=next_stage, sport_type=sport_type)


def no_tests_response(next_stage):
    return JsonResponse({
        "success": False,
        "errors": {"next_stage": [
            f"В справочнике нет испытаний для этапа «{next_stage}» "
            f"и выбранного вида спорта. Сначала добавьте испытания."
        ]},
    }, status=400)


def sync_assessment_results(assessment):
    # Приводит строки результатов в соответствие с КПИ: добавляет недостающие
    # (спортсмен x испытание) и убирает пустые строки от испытаний, которых
    # больше нет в этапе/виде спорта КПИ. Уже внесённые результаты не удаляются.
    tests = list(stage_tests(assessment.next_stage, assessment.sport_type))
    test_ids = {t.id for t in tests}
    student_ids = set(
        CustomUser.objects.filter(current_groups__group=assessment.group)
        .values_list('id', flat=True)
    )
    existing = AssessmentResult.objects.filter(assessment=assessment)

    existing.filter(result='empty').exclude(test_item_id__in=test_ids).delete()
    existing.filter(result='empty').exclude(athlete_id__in=student_ids).delete()

    have = set(existing.values_list('athlete_id', 'test_item_id'))
    AssessmentResult.objects.bulk_create([
        AssessmentResult(assessment=assessment, athlete_id=a, test_item=t, result='empty')
        for a, t in product(student_ids, tests)
        if (a, t.id) not in have
    ])


@role_required('Администратор')
def add_assessment(request):
    form = AssessmentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        # Результаты создаются только для испытаний выбранного вида спорта и этапа.
        # Если таких нет - КПИ получился бы пустым (без колонок и без возможности
        # внести результат), поэтому не сохраняем и объясняем причину.
        if not stage_tests(form.cleaned_data['next_stage'], form.cleaned_data['sport_type']).exists():
            return no_tests_response(form.cleaned_data['next_stage'])

        assessment = form.save()
        sync_assessment_results(assessment)
        return JsonResponse(
            {
                "success": True,
                "assessment": {
                    "id": assessment.id,
                    "name": assessment.name,
                    "coach": assessment.coach.get_short_name(),
                    "group": assessment.group.group_name,
                    "sport_type": (
                        assessment.sport_type.name if assessment.sport_type else None
                    ),
                    "date_start": assessment.date_start.strftime("%Y-%m-%d"),
                    "date_end": assessment.date_end.strftime("%Y-%m-%d"),
                },
            }
        )

    return JsonResponse({"success": False, "errors": form.errors}, status=400)

@role_required('Администратор')
def get_assessment(request, pk):
    assessment = get_object_or_404(Assessment, pk=pk)

    return JsonResponse(
        {
            "id": assessment.id,
            "name": assessment.name,
            "coach": assessment.coach.id,
            "group": assessment.group.id,
            "sport_type": (
                assessment.sport_type.id if assessment.sport_type else None
            ),
            "next_stage": assessment.next_stage,
            "date_start": assessment.date_start,
            "date_end": assessment.date_end,
        }
    )

@role_required('Администратор')
def edit_assessment(request, pk):
    assessment_data = get_object_or_404(Assessment, pk=pk)
    form = AssessmentForm(request.POST or None, instance=assessment_data)

    if request.method == "POST" and form.is_valid():
        if not stage_tests(form.cleaned_data['next_stage'], form.cleaned_data['sport_type']).exists():
            return no_tests_response(form.cleaned_data['next_stage'])

        assessment = form.save()
        # Этап, вид спорта или группа могли измениться - синхронизируем результаты
        sync_assessment_results(assessment)
        return JsonResponse(
            {
                "success": True,
                "assessment": {
                    "id": assessment.id,
                    "name": assessment.name,
                    "coach": assessment.coach.get_short_name(),
                    "group": assessment.group.group_name,
                    "sport_type": (
                        assessment.sport_type.name if assessment.sport_type else None
                    ),
                    "date_start": assessment.date_start.strftime("%Y-%m-%d"),
                    "date_end": assessment.date_end.strftime("%Y-%m-%d"),
                },
            }
        )
    return JsonResponse({"success": False, "errors": form.errors}, status=400)

@require_POST
@role_required('Администратор')
def delete_assessment(request, pk):
    assessment_data = get_object_or_404(Assessment, pk=pk)
    assessment_data.delete()
    return HttpResponse()
