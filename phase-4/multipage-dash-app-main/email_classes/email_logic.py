import email
import imaplib
import smtplib
import datetime

class EmailController:
    def __init__(self, server, user, password, subject):
        self.server = server
        self.user = user
        self.password = password
        self.subject = subject
        self.sent = False
        self.received = False

    def send_email(self, msg):
        
        message =  """From: <{sndr}>
To: Smarthome User <{rcv}>
Subject: {sbjt}

{ctnt}""".format(sndr=self.user, rcv=self.user, sbjt=self.subject, ctnt=msg)

        try:
            # sending email
            smtpObj = smtplib.SMTP(self.server)
            
            # sender and receiver are same email, but email message contains <Smarthome User> as sender
            smtpObj.sendmail(self.user, self.user, message)
            
            print (f"Message '{msg}' sent to {self.user}")
            
        except smtplib.SMTPException:
            print ("Could not send email")
        
    # returns a value depending on response from email
    # 0 -> no
    # 1 -> yes
    # 2 -> bad response
    # 3 -> waiting for response
    def check_email_response(self):
        
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
        
        rev_ids = mail_ids[::-1]
        
        for i in rev_ids:
        
            status, data = inbox.fetch(i, "(RFC822)")
            
            for response_part in data:
                if isinstance(response_part, tuple):
                    recieved_message = email.message_from_bytes(response_part[1])
                    
                    # checking sender and receiver
                    # TODO IF ITS FROM THE CODE THEN EXIT LOOP AND RETURN 3
                    mail_sender = recieved_message["from"]
                    mail_receiver = recieved_message["to"]
                    
                    if ("Smarthome User" in mail_receiver):
                        return 3
                    
                    # filtering for specified sender, which is ourselves
                    if self.user in mail_sender:
                        
                        # checking subject, checking for temp or for lights
                        mail_subject = recieved_message["subject"]
                        
                        if (self.subject in mail_subject):
                            # checking content 
                            if recieved_message.is_multipart():
                                mail_content = ''

                                for part in recieved_message.get_payload():
                                    if part.get_content_type() == "text/plain":
                                        mail_content += part.get_payload()
                            else:
                                mail_content = recieved_message.get_payload()
                            
                            # check mail content with or without caps
                            filter = "YES"
                            if (filter.casefold() in mail_content.casefold()):
                                # print mail
                                print(f"From: {mail_sender}")
                                print(f"To: {mail_receiver}")
                                print(f"Subject: {mail_subject}")
                                print(f"Content: {mail_content}")
                                
                                self.received = True
                                return 1
                            
                            filter = "NO"
                            if (filter.casefold() in mail_content.casefold()):
                                # print mail
                                print(f"From: {mail_sender}")
                                print(f"To: {mail_receiver}")
                                print(f"Subject: {mail_subject}")
                                print(f"Content: {mail_content}")
                                
                                self.received = True
                                return 0
                            
                            #do not change received or else it will stop looking when bad response   
                            return 2
                   
                   #once you have the check to see if its from user or from code
                    # then you can return 3
                   
    def test(self):
        print(self.sent)
        print(self.received)