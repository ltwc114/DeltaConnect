import smtblib

server = smtplib.SMTP( "smtp.gmail.com", 587 )
server.starttls()
server.login( '<gmail_address>', '<gmail_password>' )

server.sendmail( '<from>', '<number>@tmomail.net', '<msg>' )



