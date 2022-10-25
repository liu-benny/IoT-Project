import smtplib


def send_email(msg, user, password):
    server = '192.168.0.11'

    message =  """From: <{sndr}>
To: Smarthome User <{rcv}>
Subject: Message sent from Python

{ctnt}""".format(sndr=user, rcv=user, ctnt=msg)

    try:
        # sending email
        smtpObj = smtplib.SMTP(server)
        
        # sender and receiver are same email, but email message contains <python_code> as sender
        smtpObj.sendmail(user, user, message)
        print (f"Message '{msg}' sent to {user}")
    except smtplib.SMTPException:
        print ("Could not send email")