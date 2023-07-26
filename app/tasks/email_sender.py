from pydantic import EmailStr

from celery import Celery
from email.message import EmailMessage
import smtplib
from .. config import settings

# create celery app
celery_mail = Celery("sender_email", broker=settings.REDIS_URL)

MAIL_HOST = settings.MAIL_SERVER
MAIL_PORT = settings.MAIL_PORT

@celery_mail.task
def send_confirm_email(user_email: EmailStr,
                       confirm_link: str,
                       user_name: str = "",
):
    """Task for celery, send the email
    to the user with link link to confirm the mail"""
    email = get_email_template(user_email, confirm_link, user_name)
    # open connection with smtp server
    with smtplib.SMTP_SSL(MAIL_HOST, MAIL_PORT) as s:
        s.login(settings.MAIL_FROM, settings.MAIL_PASSWORD)
        s.send_message(email)
        
# genegate simple template for mail
def get_email_template(user_email: EmailStr,
                        confirm_link: str,
                        user_name: str = "",
) -> EmailMessage:
    """Create email template with all needs parameters"""
    email = EmailMessage()
    email["Subject"] = "Confirm your email"
    email["From"]: str = settings.MAIL_FROM
    email["To"]: str = user_email
    email.add_header('Content-Type', 'text/html')
    email.set_content(
        '<div>'
        f'<h1>Hello {user_name}, to confirm your email, follow the link below.</h1>'
        f'<a href="{confirm_link}">Click Here</a>'
        '</div>',
        subtype='html',
) 
    return email
