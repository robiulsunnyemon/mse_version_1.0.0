from fastapi_mail import FastMail,MessageSchema,ConnectionConfig
from app.schemas.send_otp import SendOtpModel

conf=ConnectionConfig(
    MAIL_USERNAME="robiulsunyemon111@gmail.com",
    MAIL_PASSWORD= "qqir yxsd fvxb iozs",
    MAIL_FROM= "robiulsunyemon111@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)



async def send_otp(send_otp_data: SendOtpModel):
    subject = "🔑 Your OTP Code"
    body = f"""
      <h3>Hello,</h3>
      <p>Your OTP code is: <b>{send_otp_data.otp}</b></p>
      <p>This code will expire in 5 minutes.</p>
      """

    message = MessageSchema(
        subject=subject,
        recipients=[send_otp_data.email],
        body=body,
        subtype="html"
    )


    fm=FastMail(conf)
    await fm.send_message(message)