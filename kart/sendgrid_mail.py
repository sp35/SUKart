import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_mail(to_email, subject, html_content):
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        message = Mail(
        from_email=os.environ.get('SENDER_EMAIL'),
        to_emails=to_email,
        subject=subject,
        html_content=html_content)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
        return True
    except Exception as e:
        print(str(e))
        return False