"""
Mail Delivery Route
Author: Peini She
Maintainers: Zixin Ding (logic enhancement, bug fixing)

This module provides a REST API endpoint to send try-on results via email.

Features:
- Accepts base64-encoded image and target email address.
- Detects image type (jpeg/png).
- Sends email via Flask-Mail with image attachment.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_mail import Mail, Message
import base64
import imghdr

email_bp = Blueprint("email", __name__)
mail = Mail()

@email_bp.route("/send-email", methods=["POST"])
def send_email():
    """
    Send a try-on result image to the provided email address.

    JSON Input:
    {
        "email": "recipient@example.com",
        "imageBase64": "data:image/jpeg;base64,..."
    }

    Response:
    - 200 OK: success
    - 400 Bad Request: missing input
    - 500 Internal Server Error: failed to send
    """
    data = request.get_json()
    email = data.get("email")
    image_base64 = data.get("imageBase64")

    if not email or not image_base64:
        return jsonify({"success": False, "message": "Missing email or image"}), 400

    try:
        # If there's a comma, strip out the prefix (e.g., "data:image/jpeg;base64,")
        if "," in image_base64:
            image_base64 = image_base64.split(",")[1]

        # Pad base64 if needed (binascii.Error: Incorrect padding)
        missing_padding = len(image_base64) % 4
        if missing_padding:
            image_base64 += "=" * (4 - missing_padding)

        # Decode image
        image_data = base64.b64decode(image_base64)

        # Detect image type (jpeg, png, etc.)
        image_type = imghdr.what(None, h=image_data) or "jpeg"
        filename = f"tryon_result.{image_type}"

        # Optional: Save for local debug
        # with open(filename, "wb") as f:
        #     f.write(image_data)

        # Create and send email
        msg = Message(
            subject="Your Try-on Result - OVDR",
            sender=current_app.config["MAIL_USERNAME"],
            recipients=[email],
            body="Here is your try-on result. Thanks for using OVDR!"
        )

        msg.attach(
            filename,
            f"image/{image_type}",
            image_data
        )

        mail.send(msg)

        return jsonify({"success": True, "message": "Email sent successfully!"}), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error sending email: {str(e)}"
        }), 500
