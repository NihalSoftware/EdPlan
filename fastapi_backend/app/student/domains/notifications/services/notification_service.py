from app.utils.email import send_email
from app.utils.sms import send_sms


def notify_advisor(
    *,
    email: str,
    advisor_email: str,
    body: str = "",
    phone: str | None = None,
) -> None:
    send_email("Education plan", body or "Education plan update", advisor_email)
    if phone:
        send_sms(f"New education-plan request from {email}", phone)
