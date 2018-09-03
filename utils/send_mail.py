import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_mail( subj, text ):
    senderEmail = "weathercompared@gmail.com"
    empfangsEmail = "achimhoth@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = senderEmail
    msg['To'] = empfangsEmail
    msg['Subject'] = subj

    emailText = text
    msg.attach(MIMEText(emailText, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587) # Die Server Daten
    server.starttls()
    server.login(senderEmail, "=F4;hmHsHXB") # Das Passwort
    text = msg.as_string()
    server.sendmail(senderEmail, empfangsEmail, text)
    server.quit()
