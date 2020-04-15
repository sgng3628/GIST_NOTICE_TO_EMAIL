import requests,json,wget
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.utils import COMMASPACE,formatdate

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def inputEmails():
    f = open(os.path.join(BASE_DIR,"testemail.txt"))
#    f = open(os.path.join(BASE_DIR,"emails.txt"))
    emails = f.readlines()
    f.close()
    tmp = []
    for email in emails:
        tmp.append(email.strip())
    return tmp

def inputPd():
    json_file = open(os.path.join(BASE_DIR,"gmail_pd.json"))
#    json_file = open(os.path.join(BASE_DIR,"pd.json"))
    data = json.load(json_file)
    return data

def get_html(PD):
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')
    driver = webdriver.Chrome(chrome_options=options)
    driver.get('https://college.gist.ac.kr/college/login.do')
    driver.find_element_by_name('id').send_keys(PD["my_id"])
    driver.find_element_by_name('password').send_keys(PD["my_passwd"])
    driver.find_element_by_id('login_btn').click()
    driver.get('https://college.gist.ac.kr/prog/bbsArticle/BBSMSTR_000000005587/list.do')
    driver.find_elements_by_class_name('subject')[i].find_element_by_tag_name('a').click()
    html = driver.page_source
    driver.quit()
    
    return html

def extract_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    title = soup.find('h2', class_='ui bbs--view--tit').get_text().strip()[0:-2];
    date = soup.find('span', class_='date').get_text();
    content = soup.find('div', class_='ui bbs--view--content').get_text().strip();
    subject = '[학내공지] ('+ date[4:] + ') ' + title

    files = []
    for clip in soup.find_all('a',class_='btn-on-ico'):
        clip_url = 'https://college.gist.ac.kr/cmm/fms/FileDown.do?atchFileId='+clip['href'].split("'")[1]+'&fileSn='+clip['href'].split("'")[3]
        file_name = ""
        print(clip.get_text())
        for x in clip.get_text().split("[")[:-1]:
            file_name = file_name + x
        file_name = file_name.strip()
        file_path = os.path.join(BASE_DIR,"files",file_name)
        attach_file = wget.download(clip_url,file_path)
        files.append(file_path)
    return subject, content, files[0:1]

def send_mail(send_from, send_to, username, password, subject, message, files=[],server="mail.gist.ac.kr",port=465):
    msg = MIMEMultipart()
    msg['From'] = "GIST학내공지"
#    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(message))
    for path in files:
        part = MIMEBase('application',"octet-stream")
        with open(path,'rb') as f:
            part.set_payload(f.read())
            encoders.encode_base64(part)
            file_name = os.path.basename(path)
            part.add_header("Content-Disposition","attachment",filename=file_name)
            msg.attach(part)
    smtp = smtplib.SMTP_SSL(server, port)
    smtp.login(username, password)
    for to in send_to:
        print(to)
        smtp.sendmail(send_from, to, msg.as_string())
    smtp.quit()



with requests.Session() as s:
    notices = s.get('https://college.gist.ac.kr/prog/bbsArticle/BBSMSTR_000000005587/list.do')
    print("Request Success")
    html = notices.text
    soup = BeautifulSoup(html, 'html.parser')
    titles = []
    i = 0
    for notice in soup.find_all('tr', class_='notice'):
        i += 1
    latest_title = soup.select('td.subject > a')[i].get_text()
    before = ''
    with open(os.path.join(BASE_DIR,'latest.txt'),'r') as f:
        before = f.readline()
    if before != latest_title:
        with open(os.path.join(BASE_DIR, 'latest.txt'),'w') as f:
            f.write(latest_title)

            PD = inputPd()
            html = get_html(PD)
            
            subject, message, files = extract_html(html)

            send_to = inputEmails()
            send_from = PD["my_email"] 
            username = PD["my_email"]
            password = PD["my_passwd"] 

            send_mail(send_from, send_to, username, password, subject, message, files,"smtp.gmail.com")
