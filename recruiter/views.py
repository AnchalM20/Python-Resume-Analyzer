from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout as logout_auth
from django.contrib import messages
from .forms import FileUploadForm
from pyresparser import ResumeParser
from django.shortcuts import render
from .forms import FileUploadForm
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from io import StringIO
from django.contrib.auth.decorators import login_required
import time,datetime
from candidate.models import ResumeData
from candidate.views import recommended_skills_f,resume_score_tips,course_recommender
from django.contrib import messages
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from django.core.mail import send_mail


# from .Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
# import base64,random


def signin(request):
    if request.user.is_authenticated:
        messages.success(request, "You are already Logged In!")
        return redirect('/recruiter')
    else:
        if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email, password=password)
                                
            if user is not None:
                login(request, user)
                return redirect('/recruiter')
       
            else:
                messages.error(request, "Either username or password is incorrect!")
                return render(request, 'recruiterlogin.html')

            
    return render(request, 'recruiterlogin.html')


def recruiter(request):
    return render(request,'recruiter.html')

@login_required
def logout(request):
    if request.user.is_authenticated:
        logout_auth(request)
        messages.success(request,'You are successfully logged out!')
        return redirect('/')
    else:
        messages.error(request,'You are not logged in. Please Login In!')
        return redirect('/signin')


@login_required
def upload_resume_recruiter(request):
    form = FileUploadForm()

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the file here (e.g., read its content)
            pdf_file = request.FILES['file']#.read().decode('utf-8')
            
             # Save the uploaded PDF file temporarily
            with open('temp_resume.pdf', 'wb') as temp_file:
                temp_file.write(pdf_file.read())
            
            # Parse the resume using ResumeParser
            resume_data = ResumeParser('temp_resume.pdf').get_extracted_data()
            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            timestamp = str(cur_date+'_'+cur_time)
            score,tips = resume_score_tips()
            name=resume_data["name"]
            email=resume_data["email"]
            resume_score=score
            timestamp=timestamp
            page_no=resume_data["no_of_pages"]
            if float(resume_data['total_experience'])<1:
                user_level="Fresher"
            elif float(resume_data['total_experience'])>=1 and float(resume_data['total_experience'])<3:
                user_level="Intermediate"
            else:
                user_level="Senior" 

            actual_skills=str(resume_data["skills"])
            recommended_skills,predicted_field=recommended_skills_f(resume_data)
            recommended_skills=list(recommended_skills.values())[0][1]
            recommended_courses=list(course_recommender(predicted_field).values())

            resume_data = ResumeData(
            Name=name,
            Email_ID=email,
            resume_score=resume_score,
            Timestamp=timestamp,
            Page_no=page_no,
            Predicted_Field=predicted_field,
            User_level=user_level,
            Actual_skills=actual_skills,
            Recommended_skills=recommended_skills,
            Recommended_courses=recommended_courses,
            recruiter_id=request.user
            )
            resume_data.save()
            messages.success(request,"Resume has been uploaded to database successfully !")
    return render(request, 'recruiter.html', {'form': form})                 


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text


@login_required
def view_report(request):
    user = request.user  # Get the logged-in user
    resumes = ResumeData.objects.filter(recruiter_id=user)
    if resumes.count() < 1:
        context = {'no_data':"No records found in ResumeData table!"}
        return render(request, 'viewreport.html', context)
    
    plot_data = ResumeData.objects.all().values(
        'ID',
        'Name',
        'Email_ID',
        'resume_score',
        'Timestamp',
        'Page_no',
        'Predicted_Field',
        'User_level',
        'Actual_skills',
        'Recommended_skills',
        'Recommended_courses'
    )
    
    # for r in resumes:
    #     print(r.Predicted_Field)
    context = {
        'resumes': resumes,
        'pie_chart_field' : get_pie(plot_data),
        'pie_chart_exp': get_exp_pie(plot_data)
    }
    return render(request, 'viewreport.html', context)


def get_pie(plot_data):
    plt.switch_backend("AGG")

     # Convert Django queryset to a Pandas DataFrame
    plot_data_df = pd.DataFrame.from_records(plot_data)
    
    # Generate the pie chart
    labels = plot_data_df['Predicted_Field'].unique()
    sizes = plot_data_df['Predicted_Field'].value_counts()
    
    plt.figure(figsize=(5, 4))
    plt.pie(sizes, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    plt.legend(title="Predicted Fields", labels=labels, loc="upper right", bbox_to_anchor=(1.1,0.3))
    plt.title("Predicted Field Recommendations")
    graph = get_graph()
    return graph


# best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'
def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph


def get_exp_pie(plot_data):
    plt.switch_backend("AGG")

    # Convert Django queryset to a Pandas DataFrame
    plot_data_df = pd.DataFrame.from_records(plot_data)
    # Generate the pie chart
    labels = plot_data_df['User_level'].unique()
    sizes = plot_data_df['User_level'].value_counts()
    
    plt.figure(figsize=(5, 4))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    plt.legend(title="Experience Levels", labels=labels, loc="upper right", bbox_to_anchor=(1.1, 1))
    plt.title("Exper Field Recommendations")

    graph = get_graph()
    return graph


def delete_resumes(request,email):
    ResumeData.objects.filter(Email_ID=email).delete()
    messages.success(request,"resume of candidate" + email + "has been deleted!")
    return redirect('upload_resume_recruiter')   


def send_mail_to_candidate(request,email, job_role):
    subject = 'Hiring For ' + job_role
    message = "Hi, \nI hope this email finds you well. We were impressed by your qualifications and skills, and we are excited to invite you for an interview for the " + job_role+" position at our company\n\nPlease confirm your availability for the scheduled interview\n\nIf you have any questions or need to reschedule, please don't hesitate to contact us at "+request.user.email+"\n\nWe look forward to meeting you and exploring the opportunity of having you join our team."+"\n\nBest regards,\n\n"+request.user.email
    from_email = request.user.email
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    messages.success(request,"email has been sent to the " + email)
    return redirect('view_report')     

