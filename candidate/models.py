from django.db import models
from recruiter.models import registeredUser

# Create your models here.

class ResumeData(models.Model):
    ID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100)
    Email_ID = models.CharField(max_length=50)
    resume_score = models.CharField(max_length=8)
    Timestamp = models.CharField(max_length=50)
    Page_no = models.CharField(max_length=5)
    Predicted_Field = models.CharField(max_length=50)
    User_level = models.CharField(max_length=30)
    Actual_skills = models.CharField(max_length=1000)
    Recommended_skills = models.CharField(max_length=1000)
    Recommended_courses = models.CharField(max_length=1000)
    recruiter_id = models.ForeignKey(registeredUser,on_delete=models.CASCADE,null=True)

  




