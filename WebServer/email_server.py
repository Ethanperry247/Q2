import smtplib, ssl

class EmailServer():

    def __init__(self, receiver_email):
        super().__init__()
        self.smtp_server = "smtp.gmail.com"
        self.port = 587  # For starttls
        self.sender_email = "alpineemailserver@gmail.com"
        self.password = "tPmcuZopO48uzAL1fliRJCIoyQKu+FCHUkcWI7pcNSA="
        self.receiver_email = receiver_email
        self.message = """\
        Subject: Daily KCup Report
        """

    def send_message(self, message):
        # Amend the message template.
        self.message = self.message + "\n\n" + message
        # Create a secure SSL context
        context = ssl.create_default_context()
        print("Sending Email...")
        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(self.smtp_server,self.port)
            server.ehlo() # Can be omitted
            server.starttls(context=context) # Secure the connection
            server.ehlo() # Can be omitted
            server.login(self.sender_email, self.password)
            for email in self.receiver_email:
                server.sendmail(self.sender_email, email, self.message)
                print(f'Email Sent to {email} Successfully!')
        except Exception as e:
            # Print any error messages to stdout
            print("Error Sending Email!")
        finally:
            server.quit() 