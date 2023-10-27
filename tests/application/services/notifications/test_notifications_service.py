from smtplib import SMTPException

import pytest

from application.services.notification_service import NotificationService
from infrastructure.smtp.mail_message.mail_message import MailMessage, Recipients, Subject, Lang, MailTemplate
from infrastructure.smtp.smtp_client import SmtpClient, MailNotSentException

smtp_config = {
    "smtp_mail_address": "test@carpendev.com",
    "password": "fenIOssKkXewl8CBWqVN",
    "smtp_server": "server694527.nazwa.pl"
}


@pytest.mark.mail
def test_should_send_mail():
    # given
    test_message = MailMessage(
        Recipients([smtp_config["smtp_mail_address"]]),
        Subject("test"), MailTemplate("mail_template", Lang.EN, {'name': 'Carpendev'}))
    mail_service = NotificationService(SmtpClient(smtp_config))

    # when
    try:
        mail_service.send_email_notification(test_message)
    except (MailNotSentException, SMTPException) as exception:
        pytest.fail()
    # then not fail
