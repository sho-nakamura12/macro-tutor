from django import forms
from .models import Student, UnitMaster, GradeChoices, DayOfWeekChoices


class StudentForm(forms.ModelForm):
    tutoring_days_checkbox = forms.MultipleChoiceField(
        choices=DayOfWeekChoices.choices,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="指導曜日（複数選択可）"
    )

    class Meta:
        model = Student
        fields = ["name", "grade", "semester_type", "start_date", "test_date", "tutoring_days_checkbox"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "test_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.tutoring_days:
            self.fields["tutoring_days_checkbox"].initial = [str(d) for d in self.instance.tutoring_days]

    def save(self, commit=True):
        student = super().save(commit=False)
        selected_days = self.cleaned_data.get("tutoring_days_checkbox", [])
        student.tutoring_days = [int(day) for day in selected_days]
        
        if commit:
            student.save()
        return student


GRADE_CHOICES = [("", "すべて")] + list(GradeChoices.choices)
SUBJECT_CHOICES = [("", "すべて")] + list(UnitMaster.Subject.choices)


class AddUnitsSearchForm(forms.Form):
    grade = forms.ChoiceField(choices=GRADE_CHOICES, required=False)
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES, required=False)


class AddUnitsSelectForm(forms.Form):
    unit_master_ids = forms.ModelMultipleChoiceField(
        queryset=UnitMaster.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    def __init__(self, *args, student=None, queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if queryset is not None:
            self.fields["unit_master_ids"].queryset = queryset
        elif student is not None:
            existing = student.units.values_list("unit_master_id", flat=True)
            self.fields["unit_master_ids"].queryset = UnitMaster.objects.exclude(id__in=existing)
