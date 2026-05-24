from django.contrib import admin
from .models import Student, Unit, UnitMaster

# Studentの表示ルールをカスタマイズします
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'grade', 'teacher') 
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(teacher=request.user)

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('student', 'unit_master', 'status')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(student__teacher=request.user)

admin.site.register(UnitMaster)