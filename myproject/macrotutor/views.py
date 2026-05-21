from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Student, Unit, UnitMaster
from .forms import (
    StudentForm,
    AddUnitsSearchForm,
    AddUnitsSelectForm,
)


@login_required
def student_list(request):
    students = Student.objects.filter(teacher=request.user)
    
    today_weekday = timezone.localtime().weekday()
    is_today_filter = request.GET.get('filter') == 'today'

    if is_today_filter:
        students = [
            student for student in students 
            if student.tutoring_days and today_weekday in student.tutoring_days
        ]

    return render(request, "macrotutor/index.html", {
        "students": students,
        "is_today_filter": is_today_filter,
    })


@login_required
def create_student_with_units(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            with transaction.atomic(): 
                student = form.save(commit=False)
                student.teacher = request.user
                student.save()
                
                selected_ids = request.POST.getlist("unit_master_ids")
                
                if selected_ids:
                    masters = UnitMaster.objects.filter(id__in=selected_ids)
                    to_create = [
                        Unit(student=student, unit_master=m, status=Unit.Status.NOT_STARTED)
                        for m in masters
                    ]
                    if to_create:
                        Unit.objects.bulk_create(to_create)
                        
            return redirect("macrotutor:student_detail", pk=student.id)
    else:
        form = StudentForm()

    unit_masters = UnitMaster.objects.all()
    return render(request, "macrotutor/add_student.html", {
        "form": form, 
        "unit_masters": unit_masters
    })


@require_POST
@login_required
def update_unit_status(request, unit_id):
    """ HTMXからのリクエストを受け取り、ステータスを次の段階へ進める """
    unit = get_object_or_404(Unit, pk=unit_id, student__teacher=request.user)
    unit.cycle_status() 

    student = unit.student
    current_progress = student.calculate_current_progress()
    recommended_progress = student.calculate_recommended_progress()

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'macrotutor/unit_card.html', {
            'unit': unit,
            'current_progress': current_progress,
            'recommended_progress': recommended_progress,
        })

    return JsonResponse({
        'success': True,
        'current_progress': current_progress,
        'recommended_progress': recommended_progress,
    })


def unitmaster_api(request):
    grade = request.GET.get("grade")
    subject = request.GET.get("subject")
    qs = UnitMaster.objects.all()

    if grade:
        qs = qs.filter(grade=grade)
    if subject:
        qs = qs.filter(subject=subject)

    data = [{"id": m.id, "unit_name": m.unit_name} for m in qs]
    return JsonResponse(data, safe=False)


@login_required
def student_detail(request, pk):
    student = get_object_or_404(Student, id=pk, teacher=request.user)
    units = Unit.objects.filter(student=student).select_related("unit_master")

    return render(request, "macrotutor/student_detail.html", {
        "student": student,
        "units": units,
    })


@login_required
def delete_unit(request, pk, unit_id):
    """ 同期削除（フォーム送信用） """
    student = get_object_or_404(Student, id=pk, teacher=request.user)
    unit = get_object_or_404(Unit, id=unit_id, student=student)

    if request.method == "POST":
        unit.delete()
        return redirect("macrotutor:student_detail", pk=student.id)

    return redirect("macrotutor:student_detail", pk=student.id)


@login_required
def add_unit(request, pk):
    """ 単体追加 """
    student = get_object_or_404(Student, id=pk, teacher=request.user)
    existing_master_ids = student.units.values_list("unit_master_id", flat=True)

    grade = request.GET.get("grade")
    subject = request.GET.get("subject")

    units = UnitMaster.objects.exclude(id__in=existing_master_ids)
    grades = UnitMaster.objects.values_list("grade", flat=True).distinct()
    subjects = UnitMaster.objects.values_list("subject", flat=True).distinct()

    if grade:
        units = units.filter(grade=grade)
    if subject:
        units = units.filter(subject=subject)

    if request.method == "POST":
        master_id = request.POST.get("unit_master_id")
        if master_id:
            if not student.units.filter(unit_master_id=master_id).exists():
                Unit.objects.create(
                    student=student,
                    unit_master_id=master_id,
                    status=Unit.Status.NOT_STARTED
                )
        return redirect("macrotutor:student_detail", pk=student.id)

    return render(request, "macrotutor/add_unit.html", {
        "student": student,
        "grades": grades,
        "subjects": subjects,
        "selected_grade": grade,
        "selected_subject": subject,
        "units": units,
    })


@login_required
def edit_student(request, pk):
    student = get_object_or_404(Student, id=pk, teacher=request.user)

    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f"{student.name} さんの情報を更新しました！")
            return redirect("macrotutor:student_detail", pk=student.id)
    else:
        form = StudentForm(instance=student)

    return render(request, "macrotutor/edit_student.html", {
        "student": student,
        "form": form,
    })


@require_POST
@login_required
def delete_student(request, pk):
    student = get_object_or_404(Student, id=pk, teacher=request.user)
    student_name = student.name
    student.delete()
    
    messages.success(request, f"🗑️ {student_name} さんのデータを削除しました。")
    return redirect("macrotutor:student_list")


@require_POST
@login_required
def delete_all_units(request, pk):
    student = get_object_or_404(Student, id=pk, teacher=request.user)
    deleted_count, _ = Unit.objects.filter(student=student).delete()
    
    messages.success(request, f"🗑️ 定期テストお疲れ様でした！ {deleted_count}件の単元をリセットしました。")
    return redirect("macrotutor:student_detail", pk=pk)


@require_POST
@login_required
def delete_unit_ajax(request, pk):
    unit = get_object_or_404(Unit, id=pk, student__teacher=request.user)
    unit.delete()
    return JsonResponse({"success": True})


@login_required
def add_units(request, pk):
    student = get_object_or_404(Student, id=pk, teacher=request.user)
    search_form = AddUnitsSearchForm(request.GET or None)
    queryset = UnitMaster.objects.all()

    if search_form.is_valid():
        grade = search_form.cleaned_data.get("grade")
        subject = search_form.cleaned_data.get("subject")
        if grade:
            queryset = queryset.filter(grade=grade)
        if subject:
            queryset = queryset.filter(subject=subject)

    existing_ids = set(student.units.values_list("unit_master_id", flat=True))
    candidates = queryset.exclude(id__in=existing_ids)

    if request.method == "POST":
        select_form = AddUnitsSelectForm(request.POST, student=student, queryset=candidates)
        if select_form.is_valid():
            selected = select_form.cleaned_data["unit_master_ids"]
            to_create = []
            
            for um in selected:
                if um.id not in existing_ids:
                    to_create.append(Unit(student=student, unit_master=um, status=Unit.Status.NOT_STARTED))
            
            if to_create:
                Unit.objects.bulk_create(to_create)
            return redirect("macrotutor:student_detail", pk=student.id)
    else:
        select_form = AddUnitsSelectForm(student=student, queryset=candidates)

    return render(request, "macrotutor/add_units.html", {
        "student": student,
        "search_form": search_form,
        "select_form": select_form,
        "candidates": candidates,
    })