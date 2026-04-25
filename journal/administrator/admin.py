from django.contrib import admin
from .models import *

admin.site.register(Coach)
admin.site.register(TrainingType)
admin.site.register(Hall)
admin.site.register(Slot)
admin.site.register(Group)
admin.site.register(StudentGroup)
admin.site.register(WeekDay)
admin.site.register(Schedule)
admin.site.register(Competition)
admin.site.register(Assessment)
admin.site.register(TestItem)
admin.site.register(AssessmentResult)

# Register your models here.
