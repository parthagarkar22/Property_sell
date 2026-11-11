# Property_sell
# Baba Khatu Shyam Real Estate

Django website for a local property broker across **Vidarbha, Maharashtra**.

## Features

- Browse properties freely (no login)
- Photos, sq ft, price per sq ft, YouTube video, Maps link
- Call / WhatsApp buttons
- “I’m Interested” → register/login with mobile + password → alert to broker
- My Interested Properties for customers
- Admin: properties + interest list with New / Called / Closed

## Quick start

```bash
cd "d:\My project\Property_sell"
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/  
**Broker dashboard:** http://127.0.0.1:8000/dashboard/login/

Customers register with **mobile number + password** (no OTP).

## Father’s role (custom dashboard)

1. Open `/dashboard/login/`
2. Login with broker phone + password
3. **Add property** — photos, price, location, YouTube, Maps
4. Open **Interests** — call customer, mark New / Called / Closed

Default broker account (change password after first login):
- Phone: `9834034104`
- Password: `admin123`
