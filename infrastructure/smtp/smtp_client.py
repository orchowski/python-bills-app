import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from infrastructure.smtp.mail_message.get_template import render_template
from infrastructure.smtp.mail_message.mail_message import MailMessage


class SmtpClient:

    def __init__(self, smtp_config):
        self.sender_email = smtp_config["smtp_mail_address"]
        self.password = smtp_config["password"]
        self.smtp_server = smtp_config["smtp_server"]

    def send_mail(self, mail_message: MailMessage):
        recipients = mail_message.recipients

        message = MIMEMultipart("alternative")
        message["Subject"] = mail_message.subject.subject
        message["From"] = self.sender_email
        message["To"] = ", ".join(recipients.recipients)

        body = render_template(mail_message.template)

        message.attach(MIMEText(body, "html"))
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, 465, context=context) as server:
            server.login(self.sender_email, self.password)
            senderrs = server.sendmail(
                self.sender_email, recipients.recipients, message.as_string()
            )
            if len(senderrs) > 0:
                raise MailNotSentException(senderrs)


class MailNotSentException(Exception):
    pass
