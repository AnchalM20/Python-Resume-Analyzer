from django.contrib import admin
from django.urls import path
from recruiter import views

urlpatterns = [
    path('signin',views.signin,name="signin"),
    path('delete_resumes/<str:email>',views.delete_resumes,name="delete_resumes"),
    path('recruiter',views.upload_resume_recruiter,name="upload_resume_recruiter"),
    path('viewreport/', views.view_report, name='view_report'),
    path('logout',views.logout,name="logout"),
    path('send_mail/<str:email>/<str:job_role>',views.send_mail_to_candidate,name="send_mail_to_candidate")
]