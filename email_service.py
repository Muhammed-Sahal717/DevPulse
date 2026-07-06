import os

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

# Load environment variables from .env file
load_dotenv()

print("Loaded environment variables:")
print(f".env debugging: {os.getenv('MAIL_USERNAME')}")
# 1. Gather secure email configurations from our local runtime shell environment
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", ""),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", ""),
    MAIL_FROM=os.getenv("MAIL_FROM", ""),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", ""),
    MAIL_FROM_NAME="DevPulse Security Engine",
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "True") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "False") == "True",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


async def send_reset_password_email(email_to: str, token: str):
    """Asynchronously dispatches a formatted HTML password recovery link to the user."""
    # 2. Build the production URL link that your React frontend will host
    # For now, we direct them to a placeholder frontend route passing the query token
    reset_link = f"http://localhost:3000/reset-password?token={token}"

    # 3. Design an attractive, clear HTML message layout frame
    html_content = f"""
    <h3>DevPulse Password Reset Request</h3>
    <p>We received a request to reset your password. Click the secure link below to proceed:</p>
    <p><a href="{reset_link}" style="padding: 10px 20px; background-color: #0284c7; color: white; text-decoration: none; border-radius: 5px;">Reset My Password</a></p>
    <p>This secure link will expire in 15 minutes.</p>
    <p>If you did not make this request, you can safely ignore this email.</p>
    """

    # 4. Construct the payload container wrapper
    message = MessageSchema(
        subject="DevPulse Account Recovery Token",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html,
    )

    # 5. Hand off the message structure to FastMail to execute the asynchronous sending thread
    fm = FastMail(conf)
    await fm.send_message(message)
