from local_schwab_api import generate_totp
import pyotp

'''

Use to generate security for Schwab for easy login
'''
symantec_id, totp_secret = generate_totp()

print("Your Credential ID is: " + symantec_id)
print("Your TOTP secret is: " + totp_secret)

totp = pyotp.TOTP(totp_secret)
print('Your Security Code is:', str(totp.now()))
