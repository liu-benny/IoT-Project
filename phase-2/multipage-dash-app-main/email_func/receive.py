import email
import imaplib

def check_email(filter, user, password):
    server = '192.168.0.11'

    # connect to the server and go to its inbox
    inbox = imaplib.IMAP4_SSL(server)
    inbox.login(user, password)
    inbox.select("inbox")

    # get emails
    status, data = inbox.search(None, "ALL")

    # splitting data blocks
    mail_ids = []
    for block in data:
        mail_ids += block.split()

    # preparing in case no email for specificed filter
    hasMail = False

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
                    return True
                else:
                    return False
    
