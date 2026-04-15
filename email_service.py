"""
email_service.py – Send price alert emails and check all active alerts.

Call check_and_send_alerts() from a route or a scheduled job.
"""

from flask import render_template_string, url_for
from flask_mail import Message
from extensions import mail


# ── HTML email template ──────────────────────────────────────────────────────
ALERT_EMAIL_HTML = """
<!DOCTYPE html>
<html>
<body style="font-family:Inter,Arial,sans-serif;background:#f4f6fb;margin:0;padding:0;">
<div style="max-width:560px;margin:40px auto;background:#fff;border-radius:16px;
            overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">

  <!-- Header -->
  <div style="background:#1a1f36;padding:28px 32px;">
    <h1 style="color:#fff;margin:0;font-size:1.4rem;font-weight:800;">
      🏷️ Hamro<span style="color:#f97316;">Price</span>
    </h1>
    <p style="color:rgba(255,255,255,0.6);margin:4px 0 0;font-size:0.85rem;">
      Price Alert Notification
    </p>
  </div>

  <!-- Body -->
  <div style="padding:32px;">
    <p style="color:#2d3748;font-size:1rem;margin-top:0;">
      Hi <strong>{{ user_name }}</strong>,
    </p>
    <p style="color:#718096;">
      Great news! The price for a product you're watching has dropped below your target.
    </p>

    <!-- Product card -->
    <div style="background:#fff7ed;border:1px solid #fed7aa;border-radius:12px;
                padding:20px;margin:20px 0;">
      <h2 style="color:#1a1f36;font-size:1.1rem;margin:0 0 12px;">
        {{ product_name }}
      </h2>
      <table style="width:100%;border-collapse:collapse;">
        <tr>
          <td style="color:#718096;font-size:0.85rem;padding:4px 0;">Your Target</td>
          <td style="text-align:right;font-weight:600;color:#2d3748;">
            Rs. {{ target_price }}
          </td>
        </tr>
        <tr>
          <td style="color:#718096;font-size:0.85rem;padding:4px 0;">Current Price</td>
          <td style="text-align:right;font-weight:800;color:#f97316;font-size:1.1rem;">
            Rs. {{ current_price }}
          </td>
        </tr>
        <tr>
          <td style="color:#718096;font-size:0.85rem;padding:4px 0;">Available at</td>
          <td style="text-align:right;font-weight:600;color:#16a34a;">{{ seller_name }}</td>
        </tr>
      </table>
    </div>

    <a href="{{ product_url }}"
       style="display:inline-block;background:#f97316;color:#fff;text-decoration:none;
              padding:12px 28px;border-radius:8px;font-weight:700;font-size:0.95rem;">
      View Product →
    </a>

    <p style="color:#a0aec0;font-size:0.78rem;margin-top:28px;">
      You're receiving this because you set a price alert on Hamro Price.<br>
      To manage your alerts, visit your
      <a href="{{ profile_url }}" style="color:#f97316;">profile page</a>.
    </p>
  </div>

  <!-- Footer -->
  <div style="background:#f8f9fc;padding:16px 32px;text-align:center;">
    <p style="color:#a0aec0;font-size:0.75rem;margin:0;">
      © 2025 Hamro Price – Nepal's Price Comparison Platform
    </p>
  </div>
</div>
</body>
</html>
"""


def send_alert_email(user, product, current_price, seller_name, product_url, profile_url):
    """Send a single price drop alert email."""
    try:
        html_body = render_template_string(
            ALERT_EMAIL_HTML,
            user_name=user.name,
            product_name=product.name,
            target_price=f'{user_alert_target(user, product):,.0f}',
            current_price=f'{current_price:,.0f}',
            seller_name=seller_name,
            product_url=product_url,
            profile_url=profile_url,
        )
        msg = Message(
            subject=f'🔔 Price Drop: {product.name} is now Rs. {current_price:,.0f}',
            recipients=[user.email],
            html=html_body,
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f'[Email] Failed to send to {user.email}: {e}')
        return False


def user_alert_target(user, product):
    """Helper to get the user's target price for a product."""
    from models import PriceAlert
    alert = PriceAlert.query.filter_by(
        user_id=user.id, product_id=product.id, is_active=True
    ).first()
    return alert.target_price if alert else 0


def check_and_send_alerts(app):
    """
    Check all active alerts against current prices.
    Send email if price has dropped to or below target.
    Marks alert as inactive after triggering.

    Call this from a route or schedule it (e.g. APScheduler / cron).
    """
    with app.app_context():
        from models import PriceAlert, Price

        active_alerts = PriceAlert.query.filter_by(is_active=True).all()
        sent_count = 0

        for alert in active_alerts:
            # Get current lowest price for this product
            best_price = (
                Price.query
                .filter_by(product_id=alert.product_id)
                .order_by(Price.price.asc())
                .first()
            )

            if not best_price:
                continue

            if best_price.price <= alert.target_price:
                product_url = url_for(
                    'product.product_detail',
                    product_id=alert.product_id,
                    _external=True
                )
                profile_url = url_for('user.profile', _external=True)

                success = send_alert_email(
                    user=alert.user,
                    product=alert.product,
                    current_price=best_price.price,
                    seller_name=best_price.seller.name,
                    product_url=product_url,
                    profile_url=profile_url,
                )

                if success:
                    alert.is_active = False  # deactivate after sending
                    sent_count += 1

        from extensions import db
        db.session.commit()
        return sent_count
