from django.shortcuts import render
from .forms import FileUploadForm
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from io import StringIO
from .Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import base64,random

def upload_resume(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the file here (e.g., read its content)
            pdf_file = request.FILES['file']#.read().decode('utf-8')
            
            # Save the uploaded PDF file temporarily
            with open('temp_resume.pdf', 'wb') as temp_file:
                temp_file.write(pdf_file.read())
            
            resume_whole_data = pdf_reader('temp_resume.pdf')

            # Parse the resume using ResumeParser
            resume_data = ResumeParser('temp_resume.pdf').get_extracted_data()

            if resume_data:
                score,tips=resume_score_tips()
                recommend_skill,reco_field = recommended_skills_f(resume_data)
                recommend_skill_list = list(recommend_skill.values())[0]
                # print("recommend_skill_list: ",recommend_skill_list)
                temp_list = []
                if(len(recommend_skill_list[1])>10):
                    temp_list.append(recommend_skill_list[0])
                    temp_list.append(recommend_skill_list[1][:10])
                    recommend_skill_list = temp_list

                course_rec = {}

                for key,val in recommend_skill.items():
                    course_rec = course_recommender(key)
                video_link = 'https://www.youtube.com/watch?v=KJXNO7OkDbM'
                resume_text = {
                    'name' : resume_data['name'], 
                    'email':resume_data['email'],
                    'mobile':resume_data['mobile_number'],
                    'no_of_pages':resume_data['no_of_pages'],
                    'skills':resume_data['skills'],
                    'total_experience':float(resume_data['total_experience']),
                    'resume_whole_data':resume_whole_data,
                    'tips':tips,
                    'recommend_skill_list':recommend_skill_list,
                    'course_rec':course_rec,
                    'resume_score':score,
                    'video_id': video_link.split('=')[1]}
            else:
                resume_text = "something went wrong!!"
            
            return render(request, 'report.html',resume_text); 

    else:
        form = FileUploadForm()

    return render(request, 'home.html', {'form': form})

    
def resume_score_tips():
    resume_whole_data = pdf_reader('temp_resume.pdf')
    tips = {}
    resume_score = 0
    if 'Objective' in resume_whole_data:
        resume_score = resume_score+20
        tips['Objective'] ="Awesome! You have added Objective"
    else:
        tips['Objective']= "According to our recommendation please add your career objective, it will give your career intension to the Recruiters."

    if 'Declaration'  in resume_whole_data:
        resume_score = resume_score + 20
        tips['Declaration']= "Awesome! You have added Delcaration✍"
    else:
        tips['Declaration']= "According to our recommendation please add Declaration✍. It will give the assurance that everything written on your resume is true and fully acknowledged by you"

    if 'Hobbies' or 'Interests'in resume_whole_data:
        resume_score = resume_score + 20
        tips['Hobbies']= "Awesome! You have added your Hobbies⚽"
    else:
        tips['Hobbies']= " According to our recommendation please add Hobbies⚽. It will show your persnality to the Recruiters and give the assurance that you are fit for this role or not."

    if 'Achievements' in resume_whole_data:
        resume_score = resume_score + 20
        tips['Achievements']= "Awesome! You have added your Achievements🏅"
    else:
        tips['Achievements']= " According to our recommendation please add Achievements🏅. It will show that you are capable for the required position."

    if 'Projects' in resume_whole_data:
        resume_score = resume_score + 20
        tips['Projects']= "Awesome! You have added your Projects👨‍💻"
    else:
        tips['Projects']="According to our recommendation please add Projects👨‍💻. It will show that you have done work related the required position or not."
    
    return (resume_score,tips)    




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


def recommended_skills_f(resume_data):    
    #recommendation
    ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
    web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                    'javascript', 'angular js', 'c#', 'flask','html','css','Javascript','sql']
    android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
    ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
    uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
    
    recommended_skills = {}
    reco_field = ''
    for i in resume_data['skills']:
        ## Data science recommendation
        if i.lower() in ds_keyword:
            # print(i.lower())
            reco_field = 'Data Science'
            temp =[]
            temp.append("Our analysis says you are looking for Data Science Jobs.**")
            temp.append(['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit'])
            recommended_skills[reco_field]=temp
            return recommended_skills,reco_field
        
        ## Web development recommendation
        elif i.lower() in web_keyword:
            # print(i.lower())
            reco_field = 'Web Development'
            temp =[]
            temp.append("Our analysis says you are looking for Web Development Jobs.**")
            temp.append(['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK'])
            recommended_skills[reco_field]=temp            
            return recommended_skills,reco_field
        
        ## Android App Development
        elif i.lower() in android_keyword:
            # print(i.lower())
            reco_field = 'Android Development'
            temp =[]
            temp.append("Our analysis says you are looking for Android App Development Jobs.**")
            temp.append(['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite'])
            recommended_skills[reco_field]=temp
            return recommended_skills,reco_field
        
        ## IOS App Development
        elif i.lower() in ios_keyword:
            # print(i.lower())
            reco_field = 'IOS Development'
            temp =[]
            temp.append("Our analysis says you are looking for IOS App Development Jobs.**")
            temp.append(['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout'])
            recommended_skills[reco_field]=temp
            return recommended_skills,reco_field

        ## Ui-UX Recommendation
        elif i.lower() in uiux_keyword:
            # print(i.lower())
            reco_field = 'UI-UX Development'
            temp =[]
            temp.append("Our analysis says you are looking for UI-UX Development Jobs.**")
            temp.append(['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research'])
            recommended_skills[reco_field]=temp
            return recommended_skills,reco_field
            
        
def course_recommender(reco_field):
    no_of_reco_default = 4

    # if request.method == 'POST':
    #     no_of_reco = int(request.POST.get('no_of_reco', no_of_reco_default))
    # else:
    #     no_of_reco = no_of_reco_default
    rec_course = []
    course_list = {}
    c=-1
    if reco_field=='Web Development':
        random.shuffle(web_course)
        for c_name, c_link in ds_course:
            c += 1
            # print("C_Link:  ",c_link)
            #st.markdown(f"({c}) [{c_name}]({c_link})")
            rec_course.append(c_name)
            rec_course.append(c_link)
            if c == no_of_reco_default:
                break
            course_list[c_link]=c_name
        return course_list

    elif reco_field=='Data Science':
        random.shuffle(ds_course)
        for c_name, c_link in ds_course:
            c += 1
            # print("C_Link:  ",c_link)
            #st.markdown(f"({c}) [{c_name}]({c_link})")
            rec_course.append(c_name)
            rec_course.append(c_link)
            if c == no_of_reco_default:
                break
            course_list[c_link]=c_name
        return course_list

    if reco_field=='Android Development':
        random.shuffle(android_course)
        for c_name, c_link in android_course:
            c += 1
            # print("C_Link:  ",c_link)
            #st.markdown(f"({c}) [{c_name}]({c_link})")
            rec_course.append(c_name)
            rec_course.append(c_link)
            if c == no_of_reco_default:
                break
            course_list[c_link]=c_name
        return course_list
    
    if reco_field=='IOS Development':
        random.shuffle(ios_course)
        for c_name, c_link in ios_course:
            c += 1
            # print("C_Link:  ",c_link)
            #st.markdown(f"({c}) [{c_name}]({c_link})")
            rec_course.append(c_name)
            rec_course.append(c_link)
            if c == no_of_reco_default:
                break
            course_list[c_link]=c_name
        return course_list
    
    if reco_field=='UI-UX Development':
        random.shuffle(uiux_course)
        for c_name, c_link in uiux_course:
            c += 1
            # print("C_Link:  ",c_link)
            #st.markdown(f"({c}) [{c_name}]({c_link})")
            # rec_course.append(c_name)
            # rec_course.append(c_link)
            if c == no_of_reco_default:
                break
            course_list[c_link]=c_name 
        return course_list
    
