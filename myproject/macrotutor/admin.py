from django.contrib import admin
from .models import Student, Unit, UnitMaster

admin.site.register(UnitMaster)
admin.site.register(Student)
admin.site.register(Unit)