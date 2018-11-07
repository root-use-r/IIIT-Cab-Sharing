import requests
import random
 
url = "https://www.fast2sms.com/dev/bulk"
a= random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&')
b= random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&')
c= random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&')
d= random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&')
otp=a+b+c+d
Bc="Your OTP is: " + otp
payload = "sender_id=FSTSMS&message="+Bc+"&language=english&route=p&numbers=8451912387"
headers = {
 'authorization': "8nH2jShLcMyCNUZwQIYmO5gvbzs0uxDV3Xq1eaEJG7PlRprFAovt8Fye6uTGw1QEakM5HIXYBhmLUxKR",
 'Content-Type': "application/x-www-form-urlencoded",
 'Cache-Control': "no-cache",
 }
 
response = requests.request("POST", url, data=payload, headers=headers)
 
print(response.text)