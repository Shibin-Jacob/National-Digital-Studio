from flask import Flask, render_template, request, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from pathlib import Path
from email.mime.base import MIMEBase
from email import encoders
import os


app = Flask(__name__)
DATA_FILE = Path("data/products.json")


# -----------------------------
# BASIC CONFIG
# -----------------------------
STUDIO_NAME = "National Digital Studio"
STUDIO_LOCATION = "Kunnamangalam, Kozhikode, Kerala"
KOZHIKODE_ONLY_NOTE = "Online orders currently available only within Kozhikode district."

# SMTP CONFIG – replace with your real values
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


# -----------------------------
# SIMPLE IN-MEMORY PRODUCT DATA
# -----------------------------
def load_products():
    """
    Load products from JSON file.
    Called every time so that updating products.json
    automatically updates the site on refresh.
    """
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_product_by_id(product_id: str):
    products = load_products()
    for p in products:
        if p.get("id") == product_id:
            return p
    return None

# -----------------------------
# SMTP SEND FUNCTION
# -----------------------------
def send_order_email(data: dict, files=None):
    if files is None:
        files = []

    subject = f"New Online Order – {data.get('product_name')} from {STUDIO_NAME} website"

    body = f"""
New order from {STUDIO_NAME} website:

Product:
    Name   : {data.get('product_name')}
    ID     : {data.get('product_id')}
    Price  : {data.get('product_price')} {data.get('product_unit')}
    Quantity: {data.get('quantity')}

Customer Details:
    Name       : {data.get('name')}
    Email      : {data.get('email')}
    Phone      : {data.get('phone')}
    Address    : {data.get('address_line1')}
                 {data.get('address_line2')}
    Locality   : {data.get('locality')}
    City       : {data.get('city')}
    Pincode    : {data.get('pincode')}
    Delivery   : {data.get('delivery_method')}

Custom Notes / Instructions:
    {data.get('notes')}

NOTE: Online orders are meant for Kozhikode district only.
"""

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = "thedeveloupershibin@gmail.com"
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Attach uploaded files (in memory only, not saved to disk)
    for f in files:
        if not f or f.filename == "":
            continue

        part = MIMEBase("application", "octet-stream")
        file_bytes = f.read()  # read file into memory
        part.set_payload(file_bytes)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f'attachment; filename="{f.filename}"'
        )
        msg.attach(part)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)



# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def index():
    products = load_products()
    featured = products[0] if products else None

    return render_template(
        "index.html",
        studio_name=STUDIO_NAME,
        studio_location=STUDIO_LOCATION,
        kozhi_note=KOZHIKODE_ONLY_NOTE,
        featured_product=featured,
        products=products,  # if you still use this
    )




@app.route("/shop")
def shop():
    products = load_products()
    return render_template(
        "shop.html",
        studio_name=STUDIO_NAME,
        kozhi_note=KOZHIKODE_ONLY_NOTE,
        products=products,
    )



@app.route("/product/<product_id>")
def product_page(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return redirect(url_for("shop"))
    return render_template(
        "product.html",
        studio_name=STUDIO_NAME,
        studio_location=STUDIO_LOCATION,
        kozhi_note=KOZHIKODE_ONLY_NOTE,
        product=product,
    )



@app.route("/order", methods=["POST"])
def order():
    files = request.files.getlist("design_files")
    product_id = request.form.get("product_id")
    product = get_product_by_id(product_id)
    if not product:
        return render_template("order_error.html", message="Product not found.")

    # Collect form data
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    address_line1 = request.form.get("address_line1", "").strip()
    address_line2 = request.form.get("address_line2", "").strip()
    locality = request.form.get("locality", "").strip()
    city = request.form.get("city", "").strip()
    pincode = request.form.get("pincode", "").strip()
    delivery_method = request.form.get("delivery_method", "").strip()
    quantity = request.form.get("quantity", "1").strip()
    notes = request.form.get("notes", "").strip()

    # Lightweight Kozhikode check (soft check – you can tighten if you want)
    if city and "kozhikode" not in city.lower() and "calicut" not in city.lower():
        return render_template(
            "order_error.html",
            message="Online orders are currently available only within Kozhikode district. "
                    "Please enter a Kozhikode address or contact us directly."
        )

    order_data = {
        "product_id": product["id"],
        "product_name": product["name"],
        "product_price": product["price"],
        "product_unit": product["unit"],
        "name": name,
        "email": email,
        "phone": phone,
        "address_line1": address_line1,
        "address_line2": address_line2,
        "locality": locality,
        "city": city,
        "pincode": pincode,
        "delivery_method": delivery_method,
        "quantity": quantity,
        "notes": notes,
    }

    try:
        send_order_email(order_data, files=files)
    except Exception as e:
        # In production, log this properly
        print("Error sending email:", e)
        return render_template(
            "order_error.html",
            message="Something went wrong while placing your order. Please try again or contact us directly."
        )

    return render_template(
        "order_success.html",
        studio_name=STUDIO_NAME,
        product=product,
        name=name,
        kozhi_note=KOZHIKODE_ONLY_NOTE,
    )

@app.route("/services")
def services():
    return render_template(
        "services.html",
        studio_name=STUDIO_NAME,
        studio_location=STUDIO_LOCATION,
        kozhi_note=KOZHIKODE_ONLY_NOTE,
    )


@app.route("/contact")
def contact_page():
    return render_template(
        "contact.html",
        studio_name=STUDIO_NAME,
        studio_location=STUDIO_LOCATION,
        kozhi_note=KOZHIKODE_ONLY_NOTE,
    )
    


if __name__ == "__main__":
    app.run(debug=True)
