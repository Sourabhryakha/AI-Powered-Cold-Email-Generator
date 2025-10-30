import streamlit as st
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

load_dotenv()

# Email credentials from environment
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Setup logging
logging.basicConfig(level=logging.INFO)

# Scheduler setup (Singleton)
scheduler = BackgroundScheduler()
scheduler.start()

# Function to send the email
def send_email(to_email, subject, body):
    try:
        logging.info(f"Attempting to send email to {to_email}")
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)

        logging.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False

# Function to schedule the email
def schedule_email(to_email, subject, body, schedule_time):
    scheduler.add_job(send_email, 'date', run_date=schedule_time, args=[to_email, subject, body])

# Streamlit UI
st.title("📅 Schedule an Email")

to_email = st.text_input("Recipient Email")
subject = st.text_input("Email Subject")
body = st.text_area("Email Body")
send_time = st.time_input("Choose Time (24hr format)")
send_date = st.date_input("Choose Date")

if st.button("Schedule Email"):
    if not (to_email and subject and body):
        st.warning("Please fill all fields.")
    else:
        schedule_datetime = datetime.combine(send_date, send_time)
        if schedule_datetime < datetime.now():
            st.error("Scheduled time must be in the future.")
        else:
            schedule_email(to_email, subject, body, schedule_datetime)
            st.success(f"Email scheduled for {schedule_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

if st.button("Test Send Email"):
    if send_email(to_email, subject, body):
        st.success("Test email sent.")
    else:
        st.error("Failed to send test email.")
