# pyright: reportAttributeAccessIssue=false

import random

from .models import VerificationCode


def generate_otp():
    return "".join(str(random.randint(0, 9)) for _ in range(6))


def send_otp(phone_number, code):
    print("=" * 40)
    print(f"OTP for {phone_number}: {code}")
    print("=" * 40)


def create_and_send_otp(phone_number):
    VerificationCode.objects.filter(phone_number=phone_number, is_used=False).delete()

    code = generate_otp()
    VerificationCode.objects.create(phone_number=phone_number, code=code)
    send_otp(phone_number, code)


def verify_otp(phone_number, code):
    otp = VerificationCode.objects.filter(
        phone_number=phone_number, code=code, is_used=False
    ).first()

    if not otp or otp.is_expired():
        return False

    otp.is_used = True
    otp.save(update_fields=["is_used"])
    return True
