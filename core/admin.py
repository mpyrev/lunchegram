from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.models import Company, Employee


class EmployeeInline(admin.TabularInline):
    model = Employee
    extra = 0
    # readonly_fields = ['id']
    raw_id_fields = ['user']


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    inlines = [EmployeeInline]
    list_display = ['__str__', 'invite_token', 'owner', 'total_member_count', 'online_member_count']
    list_filter = ['owner']

    def total_member_count(self, obj):
        return obj.employee_set.count()
    total_member_count.short_description = _('Total member count')

    def online_member_count(self, obj):
        return obj.employee_set.filter(state=Employee.State.online).count()
    online_member_count.short_description = _('Online member count')
