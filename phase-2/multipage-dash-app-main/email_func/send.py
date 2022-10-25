import smtplib


def send_email(msg, user, password):
    password = 'd34HqY87m6bL'
    server = 'localhost'
    # server = '192.168.0.11' AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

    message =  """From: <python_code>
To: Smarthome User <{rcv}>
Subject: Message sent from Python

{ctnt}""".format(rcv=user, ctnt=msg)

    try:
        # sending email
        smtpObj = smtplib.SMTP(server)
        
        # sender and receiver are same email, but email message contains <python_code> as sender
        smtpObj.sendmail(user, user, message)
        print (f"Message '{msg}' sent to {user}")
    except smtplib.SMTPException:
        print ("Could not send email")

