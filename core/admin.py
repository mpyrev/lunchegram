from django.contrib import admin

from core.models import Company, Employee


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 0
    # readonly_fields = ['id']
    raw_id_fields = ['user']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    inlines = [EmployeeInline]
