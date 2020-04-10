import requests,json
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def inputEmails():
    f = open(os.path.join(BASE_DIR,"emails.txt"))
    emails = f.readlines()
    f.close()
    tmp = []
    for email in emails:
        tmp.append(email.strip())
    return tmp

def inputPd():
    json_file = open(os.path.join(BASE_DIR,"pd.json"))
    data = json.load(json_file)
    return data

PD = inputPd()
TO_EMAILS= inputEmails()

with requests.Session() as s:
    notices = s.get('https://college.gist.ac.kr/prog/bbsArticle/BBSMSTR_000000005587/list.do')
#    print("Request Success")
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
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('h2', class_='ui bbs--view--tit').get_text().strip();
            date = soup.find('span', class_='date').get_text();
            content = soup.find('div', class_='ui bbs--view--content').get_text().strip();
            msg = MIMEMultipart()
            msg['Subject'] = '[학내공지] ('+ date[4:] + ') ' + title
            count = 1
            for clip in soup.find_all('a',class_='btn-on-ico'):
                clip_url = 'https://college.gist.ac.kr/cmm/fms/FileDown.do?atchFileId='+clip['href'].split("'")[1]+'&fileSn='+clip['href'].split("'")[3]
                content = content + '\n' + str(count) + '. ' + clip.get_text() + "link: " + clip_url
                count += 1
#                print(clip_url)
#                filename = 'clip.get_text()'
                
#                part = MIMEBase('application','octet-stream')
#                part.set_payload((clip_url).read())
#                encoders.encode_base64(part)
#                part.add_header('Content-Diposition','attachment;filename='+filename)
#                msg.attach(part)
            contentpart = MIMEText(content)
            msg.attach(contentpart)
   
            s_mail = smtplib.SMTP_SSL('mail.gist.ac.kr',465)
            s_mail.login(PD["my_email"],PD["my_passwd"])
#            for email in TEST_EMAIL:     
            for email in TO_EMAILS:     
                s_mail.sendmail(PD["my_email"],email,msg.as_string())
            s_mail.quit()
