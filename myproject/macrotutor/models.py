from datetime import date
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class GradeChoices(models.TextChoices):
    GRADE_1 = "GRADE_1", "1年"
    GRADE_2 = "GRADE_2", "2年"
    GRADE_3 = "GRADE_3", "3年"


class DayOfWeekChoices(models.IntegerChoices):
    MONDAY = 0, "月曜日"
    TUESDAY = 1, "火曜日"
    WEDNESDAY = 2, "水曜日"
    THURSDAY = 3, "木曜日"
    FRIDAY = 4, "金曜日"
    SATURDAY = 5, "土曜日"
    SUNDAY = 6, "日曜日"


class UnitMaster(models.Model):
    class Subject(models.TextChoices):
        MATH = "MATH", "数学"
        ENGLISH = "ENGLISH", "英語"

    subject = models.CharField(max_length=20, choices=Subject.choices)
    grade = models.CharField(max_length=20, choices=GradeChoices.choices)
    unit_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.get_subject_display()} {self.get_grade_display()} {self.unit_name}"


class Student(models.Model):
    class SemesterType(models.TextChoices):
        TWO = "TWO", "2学期制"
        THREE = "THREE", "3学期制"
        
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    name = models.CharField(max_length=100)
    grade = models.CharField(choices=GradeChoices.choices, max_length=20)
    semester_type = models.CharField(choices=SemesterType.choices, max_length=20)
    start_date = models.DateField()
    test_date = models.DateField(null=True, blank=True)
    tutoring_days = models.JSONField(
        default=list,
        blank=True,
        verbose_name="指導曜日"
    )

    def auto_test_date(self):
        """学期制に基づいて「今日以降で最も近いテスト日」を自動計算する"""
        year = self.start_date.year 

        if self.semester_type == self.SemesterType.THREE:
            base_dates = [(5, 20), (7, 10), (10, 10), (12, 5), (3, 10)]
        else:
            base_dates = [(6, 15), (9, 20), (11, 20), (3, 10)]

        possible_test_dates = [
            date(y, m, d)
            for y in (year, year + 1)
            for m, d in base_dates
        ]

        upcoming_test_dates = [day for day in possible_test_dates if day >= self.start_date]
        return min(upcoming_test_dates) if upcoming_test_dates else None

    def clean(self):
        """データの整合性を検証する（開始日とテスト日の前後関係チェック）"""
        super().clean()
        if self.start_date and self.test_date:
            if self.start_date > self.test_date:
                raise ValidationError({"test_date": "テスト日は開始日より後の日付を指定してください。"})

    def save(self, *args, **kwargs):
        """テスト日が未入力の場合に自動補完して保存する"""
        if not self.test_date:
            self.test_date = self.auto_test_date()
        super().save(*args, **kwargs)

    def calculate_current_progress(self):
        """生徒の現在の進捗率（パーセント）を算出する"""
        units = self.units.all()
        total = units.count()
        if total == 0:
            return 0
        
        total_score = sum(Unit.STATUS_SCORE[u.status] for u in units)
        return int(total_score / total * 100)

    def calculate_recommended_progress(self):
        """現在の日付に基づいた推奨進捗率を算出する"""
        today = timezone.now().date()
        total_days = (self.test_date - self.start_date).days
        if total_days <= 0:
            return 0
    
        passed_days = (today - self.start_date).days
        passed_days = max(0, min(passed_days, total_days))
        return int(passed_days / total_days * 100)
    
    def update_dates(self, start_date=None, test_date=None):
        """日付を更新し、バリデーションを実行した上で保存する"""
        if start_date:
            self.start_date = start_date
        if test_date:
            self.test_date = test_date
        else:
            self.test_date = self.auto_test_date()
        
        self.full_clean()
        self.save()

    def __str__(self):
        return self.name


class Unit(models.Model):
    """生徒ごとの単元進捗ステータスを管理するモデル"""
    class Status(models.IntegerChoices):
        NOT_STARTED = 0, '未着手'
        STARTED = 1, '着手'
        IN_PROGRESS = 2, '進行中'
        DONE = 3, '完了'

    STATUS_SCORE = {
        Status.NOT_STARTED: 0,
        Status.STARTED: 0.33,
        Status.IN_PROGRESS: 0.66,
        Status.DONE: 1,
    }

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='units')
    unit_master = models.ForeignKey(UnitMaster, on_delete=models.PROTECT)
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_STARTED)

    def score(self):
        return self.STATUS_SCORE[self.status]

    def cycle_status(self):
        """HTMX経由でのステータス更新処理（ループ対応）"""
        self.status = (self.status + 1) % 4
        self.save()

    def __str__(self):
        return f"{self.unit_master.unit_name} ({self.student.name})"