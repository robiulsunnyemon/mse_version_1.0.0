from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.schemas.send_otp import SendOtpModel
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Get credentials from environment variables with fallback
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "stewartbrown195111@gmail.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "imge bokt sjqp pkry")
MAIL_FROM = os.getenv("MAIL_FROM", "robiulsunyemon111@gmail.com")

# Email configuration - Try multiple configurations
conf_tls = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,  # Set to False to avoid certificate issues
    TIMEOUT=30
)

conf_ssl = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
    TIMEOUT=30
)


async def send_otp(send_otp_data: SendOtpModel):
    """
    Send OTP email to user with fallback configurations
    """
    # Try TLS first (port 587)
    try:
        logger.info(f"📧 Attempting to send OTP via TLS to: {send_otp_data.email}")
        await send_with_config(send_otp_data, conf_tls, "TLS")
        return

    except Exception as tls_error:
        logger.warning(f"TLS failed: {tls_error}. Trying SSL...")

        # Try SSL (port 465) as fallback
        try:
            logger.info(f"📧 Attempting to send OTP via SSL to: {send_otp_data.email}")
            await send_with_config(send_otp_data, conf_ssl, "SSL")

        except Exception as ssl_error:
            logger.error(f"SSL also failed: {ssl_error}")
            raise Exception(f"Failed to send email via both TLS and SSL: {ssl_error}")


async def send_with_config(send_otp_data: SendOtpModel, config: ConnectionConfig, config_name: str):
    """
    Send email using specific configuration
    """
    try:
        subject = "🔑 Your OTP Code - Account Verification"
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 30px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #2563eb; text-align: center; margin: 30px 0; padding: 20px; background: #f8fafc; border-radius: 8px; letter-spacing: 5px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 14px; color: #64748b; }}
                .warning {{ color: #dc2626; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🔑 Your OTP Code</h2>
                <p>Hello,</p>
                <p>Please use the following OTP code to verify your account:</p>
                <div class="otp-code">{send_otp_data.otp}</div>
                <p class="warning">⚠️ This code will expire in <strong>5 minutes</strong>.</p>
                <p>If you didn't request this code, please ignore this email.</p>
                <div class="footer">
                    <p>Best regards,<br>Your Application Team</p>
                </div>
            </div>
        </body>
        </html>
        """

        message = MessageSchema(
            subject=subject,
            recipients=[send_otp_data.email],
            body=body,
            subtype="html"
        )

        fm = FastMail(config)
        await fm.send_message(message)
        logger.info(f"✅ OTP sent successfully via {config_name} to: {send_otp_data.email}")

    except Exception as e:
        logger.error(f"❌ Failed to send OTP via {config_name}: {str(e)}")
        raise e


# Test function
async def test_email_connection():
    """
    Test email connection with current credentials
    """
    test_data = SendOtpModel(
        email=MAIL_USERNAME,  # Send test to yourself
        otp="999999"
    )

    logger.info("🧪 Testing email configuration...")
    try:
        await send_otp(test_data)
        return {"status": "success", "message": "Email configuration is working!"}
    except Exception as e:
        return {"status": "error", "message": f"Email configuration failed: {str(e)}"}
