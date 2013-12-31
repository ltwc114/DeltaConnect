# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import TwilioRestClient
import sys

# Find these values at https://twilio.com/user/account
account_sid = "ACe1dc4686ba1fa745355639d3f201292a"
auth_token = "3d890c834a4d893844286e56bcabb9ca"
client = TwilioRestClient(account_sid, auth_token)
 

msg = sys.argv[1].replace('\n', '')
msg = msg.replace(' ( ', '\n(' )
sendTo = "+1" + sys.argv[2]

message = client.messages.create(to=sendTo, from_="+19252379139",
                                     body=msg)

f = open('sms.txt', 'w')
f.write(msg)
f.close()
