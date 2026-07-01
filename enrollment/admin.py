from django.contrib import admin

from .models import Attendance, Child, GuardianProfile, HealthRecord

admin.site.register(GuardianProfile)
admin.site.register(Child)
admin.site.register(HealthRecord)
admin.site.register(Attendance)
