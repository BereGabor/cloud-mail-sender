from asyncio.log import logger
import base64
import json
import os
import traceback
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from google.cloud import logging as cloudlogging
import logging
import smtplib
from email.message import EmailMessage

lg_client = cloudlogging.Client()

lg_handler = lg_client.get_default_handler()
cloud_logger = logging.getLogger("cloudLogger")
cloud_logger.setLevel(logging.DEBUG)
#cloud_logger.addHandler(lg_handler)

def sendgrid_mail(from_mail, to_mail, subject, mail_body):
    message = Mail(
        from_email=from_mail,
        to_emails=to_mail,
        subject=subject,
        html_content=mail_body)
    try:
        sg = SendGridAPIClient('$SENDGRID_EMAIL_API_KEY')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        #log_message('ERROR', 'Exception during send mail' + traceback.format_exc())
        cloud_logger.error('Exception during send mail' + traceback.format_exc())


def smtp_mail(from_mail, to_mail, subject, mail_body):
    # config to smtp
    mailServer    = os.environ.get('MAIL_SERVER', '').strip()
    mailPort    = os.environ.get('MAIL_PORT', '').strip()
    mailLocalHost = os.environ.get('MAIL_LOCAL_HOST', '').strip()
    mailForceTls  = os.environ.get('MAIL_FORCE_TLS', '').strip()=="TRUE"
    mailDebug     = os.environ.get('MAIL_DEBUG', '').strip()=="TRUE"
    
    if not mailServer:
        mailServer='mail.smtpbucket.com'

    if not mailPort:
        mailPort=8025

    #build email object
    outboundMessage = EmailMessage()
    outboundMessage.set_content(mail_body)
    outboundMessage['Subject'] = subject
    outboundMessage['From'] = from_mail
    outboundMessage['To'] = to_mail

    # You may need to customize this flow to support your mail relay configuration.
    # Examples may include authentication, encryption, etc.

    if mailForceTls:
        smtpServer = smtplib.SMTP_SSL(host=mailServer, port=mailPort,local_hostname=mailLocalHost)
    else:
        smtpServer = smtplib.SMTP(host=mailServer, port=mailPort, local_hostname=mailLocalHost)
    try:
        if mailDebug:
            smtpServer.set_debuglevel(2)

        if (not mailForceTls) and smtpServer.has_extn('STARTTLS'):
            smtpServer.starttls()
            smtpServer.ehlo()

        smtpServer.send_message(outboundMessage)
    finally:
        smtpServer.quit()



def send_email_notification(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """


    if 'data' in event:
        pubsub_message = base64.b64decode(event['data']).decode('utf-8')
        mail_dto = json.loads(pubsub_message)
    else:
        mail_dto=event
    
    mailFrom = None
    if 'from' in mail_dto:
        mailFrom = mail_dto['from']
        cloud_logger.info('From read from request :' +  mail_dto['from'])
    else:
        mailFrom= os.environ.get('MAIL_FROM', 'noreply@yourdomain.com').strip();
        cloud_logger.info('Use default value for mail From: ' + mailFrom)

    #log_message('DEBUG', 'Send mail event :' + json.dumps(event))
    cloud_logger.debug('Send mail event :' + json.dumps(mail_dto))
    #message_json = json.loads(pubsub_message)
    
    
    #sendgrid_mail('noreply@yourdomain.com', event['to'], event['subject'], event['body'])
        

    smtp_mail(mailFrom, mail_dto['to'], mail_dto['subject'], mail_dto['body'])


    cloud_logger.debug('Mail sent: ' + json.dumps(mail_dto))
