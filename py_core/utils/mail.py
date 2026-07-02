import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailSender:
    def __init__(self, server, port, address, password):
        self.server = server
        self.port = port
        self.address = address
        self.password = password

    def send_email(self, recipient, subject, body):
        message = MIMEMultipart()
        message["From"] = self.address
        message["To"] = recipient
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(self.server, self.port) as server:
            server.starttls()
            server.login(self.address, self.password)
            server.sendmail(self.address, recipient, message.as_string())
