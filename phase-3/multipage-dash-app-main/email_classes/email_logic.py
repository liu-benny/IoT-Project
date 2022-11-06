import email
import imaplib
import smtplib

class EmailController:
    def __init__(self, server, user, password):
        self.server = server
        self.user = user
        self.password = password
        self.sent = False
        self.received = False

    def send_email(self, msg):
        message =  """From: <{sndr}>
To: Smarthome User <{rcv}>
Subject: Message sent from Python

{ctnt}""".format(sndr=self.user, rcv=self.user, ctnt=msg)

        try:
            # sending email
            smtpObj = smtplib.SMTP(self.server)
            
            # sender and receiver are same email, but email message contains <Smarthome User> as sender
            smtpObj.sendmail(self.user, self.user, message)
            print (f"Message '{msg}' sent to {user}")
            
            self.sent = True
            
        except smtplib.SMTPException:
            print ("Could not send email")
        
    def check_email(self, filter):
        
        # connect to the server and go to its inbox
        inbox = imaplib.IMAP4_SSL(self.server)
        inbox.login(self.user, self.password)
        inbox.select("inbox")

        # get emails
        status, data = inbox.search(None, "ALL")

        # splitting data blocks
        mail_ids = []
        for block in data:
            mail_ids += block.split()

        # get email and content
        
        i = mail_ids.pop()
        
        status, data = inbox.fetch(i, "(RFC822)")
        
        for response_part in data:
            if isinstance(response_part, tuple):
                recieved_message = email.message_from_bytes(response_part[1])
                
                # checking sender and receiver
                mail_sender = recieved_message["from"]
                mail_receiver = recieved_message["to"]
                
                # filtering for specified sender
                if user in mail_sender:
                    
                    # checking subject, might need to filter
                    mail_subject = recieved_message["subject"]
                    
                    # checking content 
                    if recieved_message.is_multipart():
                        mail_content = ''

                        for part in recieved_message.get_payload():
                            if part.get_content_type() == "text/plain":
                                mail_content += part.get_payload()
                    else:
                        mail_content = recieved_message.get_payload()
                    
                    if (filter in mail_content):
                        # print mail
                        print(f"From: {mail_sender}")
                        print(f"To: {mail_receiver}")
                        print(f"Subject: {mail_subject}")
                        print(f"Content: {mail_content}")
                        
                        self.received = True
                        
                        return True
                    else:
                        return False
    def test(self):
        print(self.sent)
        print(self.received)