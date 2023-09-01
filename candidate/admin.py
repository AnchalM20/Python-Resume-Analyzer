from django.contrib import admin
from .models import ResumeData

class ResumeDataAdmin(admin.ModelAdmin):
    search_fields = ["Email_ID","recruiter_id","Actual_skills",]
    list_filter = ["recruiter_id","Actual_skills"]
    list_display = ["ID","Name","Email_ID","recruiter_id","Actual_skills",]


# Register your models here.
admin.site.register(ResumeData, ResumeDataAdmin)