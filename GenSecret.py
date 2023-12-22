from schwab_api import generate_totp
import pyotp

'''

Use to generate security for Schwab for easy login
'''
symantec_id, totp_secret = generate_totp()

print("Your symantec ID is: " + symantec_id)
print("Your TOTP secret is: " + totp_secret)

totp = pyotp.TOTP(totp_secret)
print(str(totp.now()))

