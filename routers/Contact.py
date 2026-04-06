"""
routers/contact.py

Dependencies:
    pip install resend

Environment variables required:
    RESEND_API_KEY=re_6CQ8wQ5a_H7p61ZjRQQPXgmovjk6aTB6F   (from resend.com)
    CONTACT_FROM_EMAIL=noreply@yourdomain.com  (must be a verified Resend sender domain)
    CONTACT_TO_EMAIL=j43430749@gmail.com       (where submissions land)

Register in main.py:
    from routers.contact import router as contact_router
    app.include_router(contact_router)
"""

import os
import logging
import resend
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator

logger = logging.getLogger(__name__)
load_dotenv()


router = APIRouter(prefix="/contact", tags=["contact"])

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

class ContactFormIn(BaseModel):
    name: str
    email: EmailStr
    phone: str = ""
    subject: str
    message: str
    preferred_contact: str = "email"
    # ── Vehicle inquiry extras (optional, sent by InquiryModal) ──
    vehicle_title: str | None = None
    inventory_id: int | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name is required.")
        if len(v) > 120:
            raise ValueError("Name must be 120 characters or fewer.")
        return v

    @field_validator("subject")
    @classmethod
    def subject_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Subject is required.")
        return v

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message is required.")
        if len(v) > 5000:
            raise ValueError("Message must be 5 000 characters or fewer.")
        return v

    @field_validator("preferred_contact")
    @classmethod
    def preferred_contact_valid(cls, v: str) -> str:
        allowed = {"email", "phone"}
        if v not in allowed:
            raise ValueError(f"preferred_contact must be one of {allowed}.")
        return v


class ContactResponse(BaseModel):
    success: bool
    message: str


# ---------------------------------------------------------------------------
# Helper – build the HTML email body
# ---------------------------------------------------------------------------

SUBJECT_LABELS: dict[str, str] = {
    "sales": "Sales Inquiry",
    "service": "Service Appointment",
    "financing": "Financing Options",
    "test-drive": "Schedule Test Drive",
    "other": "Other",
}


def _build_html(data: ContactFormIn) -> str:
    subject_label = SUBJECT_LABELS.get(data.subject, data.subject)
    vehicle_row = ""
    if data.vehicle_title:
        vehicle_row = (
            f"<tr style='border-top:1px solid #e5e7eb'>"
            f"<td style='padding:10px 16px;color:#6b7280;border-right:1px solid #f3f4f6'>Vehicle</td>"
            f"<td style='padding:10px 16px;color:#111827;font-weight:500'>{data.vehicle_title}"
            + (f" <span style='color:#9ca3af'>(#{data.inventory_id})</span>" if data.inventory_id else "")
            + "</td></tr>"
        )
    phone_line = (
        f"<tr><td style='padding:6px 0;color:#6b7280;width:140px'>Phone</td>"
        f"<td style='padding:6px 0;color:#111827'>{data.phone}</td></tr>"
        if data.phone
        else ""
    )
    return f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f9fafb;font-family:ui-sans-serif,system-ui,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 16px">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;max-width:600px">

        <!-- Header -->
        <tr>
          <td style="background:#111827;padding:28px 32px">
            <p style="margin:0;font-size:11px;letter-spacing:2px;color:#9ca3af;text-transform:uppercase">
              AutoElite Dealership
            </p>
            <h1 style="margin:6px 0 0;font-size:20px;color:#ffffff;font-weight:600">
              New Contact Form Submission
            </h1>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:32px">
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="border:1px solid #e5e7eb;border-radius:6px;overflow:hidden;font-size:14px">
              <tr style="background:#f9fafb">
                <td colspan="2" style="padding:10px 16px;font-size:11px;letter-spacing:1px;
                                       color:#6b7280;text-transform:uppercase;font-weight:600">
                  Sender Details
                </td>
              </tr>
              <tr style="border-top:1px solid #e5e7eb">
                <td style="padding:10px 16px;color:#6b7280;width:140px;border-right:1px solid #f3f4f6">Name</td>
                <td style="padding:10px 16px;color:#111827;font-weight:500">{data.name}</td>
              </tr>
              <tr style="border-top:1px solid #e5e7eb">
                <td style="padding:10px 16px;color:#6b7280;border-right:1px solid #f3f4f6">Email</td>
                <td style="padding:10px 16px">
                  <a href="mailto:{data.email}" style="color:#111827;font-weight:500">{data.email}</a>
                </td>
              </tr>
              {"<tr style='border-top:1px solid #e5e7eb'><td style='padding:10px 16px;color:#6b7280;border-right:1px solid #f3f4f6'>Phone</td><td style='padding:10px 16px;color:#111827;font-weight:500'>" + data.phone + "</td></tr>" if data.phone else ""}
              <tr style="border-top:1px solid #e5e7eb">
                <td style="padding:10px 16px;color:#6b7280;border-right:1px solid #f3f4f6">Subject</td>
                <td style="padding:10px 16px;color:#111827;font-weight:500">{subject_label}</td>
              </tr>
                {vehicle_row}
              <tr style="border-top:1px solid #e5e7eb">
                <td style="padding:10px 16px;color:#6b7280;border-right:1px solid #f3f4f6">Prefers</td>
                <td style="padding:10px 16px;color:#111827;font-weight:500">{data.preferred_contact.capitalize()}</td>
              </tr>
            </table>

            <!-- Message -->
            <h2 style="margin:28px 0 10px;font-size:13px;letter-spacing:1px;color:#6b7280;
                        text-transform:uppercase;font-weight:600">
              Message
            </h2>
            <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:6px;
                        padding:18px 20px;font-size:14px;color:#374151;line-height:1.7;
                        white-space:pre-wrap">{data.message}</div>

            <!-- Quick reply button -->
            <div style="margin-top:28px;text-align:center">
              <a href="mailto:{data.email}?subject=Re: {subject_label}"
                 style="display:inline-block;background:#111827;color:#ffffff;
                        font-size:14px;font-weight:500;text-decoration:none;
                        padding:12px 28px;border-radius:6px">
                Reply to {data.name.split()[0]}
              </a>
            </div>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f9fafb;border-top:1px solid #e5e7eb;
                     padding:16px 32px;font-size:12px;color:#9ca3af;text-align:center">
            This email was sent from the AutoElite contact form.
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit contact form",
)
async def submit_contact_form(data: ContactFormIn) -> ContactResponse:
    api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("CONTACT_FROM_EMAIL", "noreply@yourdomain.com")
    to_email = os.getenv("CONTACT_TO_EMAIL", "j43430749@gmail.com")

    if not api_key:
        logger.error("RESEND_API_KEY is not set.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email service is not configured. Please contact support.",
        )

    resend.api_key = api_key
    subject_label = SUBJECT_LABELS.get(data.subject, data.subject)

    try:
        resend.Emails.send({
            "from": f"AutoElite Contact <{from_email}>",
            "to": [to_email],
            "reply_to": data.email,
            "subject": f"[Contact] {subject_label} – {data.name}",
            "html": _build_html(data),
        })
        logger.info("Contact email sent from %s (%s)", data.email, data.subject)
        return ContactResponse(
            success=True,
            message="Your message has been sent. We'll be in touch soon.",
        )

    except resend.exceptions.ResendError as exc: # type: ignore
        logger.error("Resend API error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to send your message. Please try again later.",
        )
    except Exception as exc:
        logger.exception("Unexpected error sending contact email: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )