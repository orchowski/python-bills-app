from infrastructure.smtp.mail_message.mail_message import MailMessage
from infrastructure.smtp.smtp_client import SmtpClient


class NotificationService:
    def __init__(self, notification_client: SmtpClient):
        self.notification_client = notification_client

    def send_email_notification(self, message: MailMessage):
        self.notification_client.send_mail(message)
