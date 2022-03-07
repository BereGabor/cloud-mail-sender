# cloud-mail-sender
Cloud function to send email based on pubsub event. 

## Event structure
Event could have standard structure, when 'data' element contain bas64 encoded request body, but can process when the pure json is the event (as test function create event in the on GCP consol)

```json
{
        "from": "sender@senderdomain.com",
        "to":"sample@gmail.com",
        "subject":"Test mail subject",
        "body":"Hello Gábor!\n \n Have a nice day! \n\n Best regards\nBere"
}
```

from is optional. If 'from' not set in request the system will use a default value.

The code get the default From value from environment variable.
```python
os.environ.get('MAIL_FROM', 'noreply@yourdomain.com').strip();
```
If env variable missing, 'noreply@yourdomain.com' will be used.

#SMTP config
The config read from ENV variables:

```python
    mailServer    = os.environ.get('MAIL_SERVER', '').strip()
    mailPort    = os.environ.get('MAIL_PORT', '').strip()
    mailLocalHost = os.environ.get('MAIL_LOCAL_HOST', '').strip()
    mailForceTls  = os.environ.get('MAIL_FORCE_TLS', '').strip()=="TRUE"
    mailDebug     = os.environ.get('MAIL_DEBUG', '').strip()=="TRUE"
```
If ENV variable not set, the mailServer and mailPort ger default values:

```
mailServer='mail.smtpbucket.com'
mailPort=8025
```
This sample use a dummy and very usefull smtp server, to avoid real mail traffic.
https://www.smtpbucket.com/emails 
