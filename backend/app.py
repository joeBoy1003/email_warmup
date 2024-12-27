from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

app = Flask(__name__)
CORS(app)

# Mock storage
accounts = []
analytics = []
recipient_store = {}  # Store recipients for each email account

scheduler = BackgroundScheduler()
scheduler.start()

# Add an email account
@app.route('/add_account', methods=['POST'])
def add_account():
    data = request.json
    email = data.get('email')
    provider = data.get('provider')
    smtp_server = data.get('smtp_server')
    port = data.get('port')
    password = data.get('password')

    if email and provider and smtp_server and port and password:
        accounts.append({
            'email': email,
            'provider': provider,
            'smtp_server': smtp_server,
            'port': port,
            'password': password
        })
        analytics.append({'email': email, 'sent': 0, 'spam': 0, 'replies': 0})
        return jsonify({'message': 'Account added successfully!'}), 201
    return jsonify({'message': 'Invalid input!'}), 400

# Set warm-up schedule
@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    data = request.json
    email = data.get('email')
    daily_limit = data.get('daily_limit')

    account = next((acc for acc in accounts if acc['email'] == email), None)
    if account:
        recipient_list = recipient_store.get(email, ["recipient@example.com"])  # Mock recipients if none uploaded
        schedule_email_sending(account, recipient_list, daily_limit)
        return jsonify({'message': 'Warm-up schedule started!'}), 200
    return jsonify({'message': 'Account not found!'}), 404

# Upload recipient list
@app.route('/recipients/upload', methods=['POST'])
def upload_recipients():
    email = request.form.get('email')  # Email account for these recipients
    file = request.files['file']

    if not file or not email:
        return jsonify({'message': 'Email and file are required!'}), 400

    recipients = [line.decode('utf-8').strip() for line in file.readlines()]
    recipient_store[email] = recipients
    return jsonify({'message': 'Recipients uploaded successfully!'}), 200

# Fetch analytics
@app.route('/analytics', methods=['GET'])
def get_analytics():
    return jsonify(analytics), 200

# Mark emails as "Not Spam"
@app.route('/engage/not_spam', methods=['POST'])
def mark_as_not_spam():
    data = request.json
    email = data.get('email')
    print(f"Mock: Marking emails as 'Not Spam' for {email}")
    return jsonify({'message': f"Marked emails as 'Not Spam' for {email}"}), 200

# Schedule email sending
def schedule_email_sending(account, recipient_list, daily_limit):
    interval = 86400 // daily_limit  # Calculate interval (seconds) between emails
    recipients_to_send = recipient_list[:daily_limit]  # Limit recipients to daily limit

    for recipient in recipients_to_send:
        scheduler.add_job(
            send_email,
            args=(account['smtp_server'], account['port'], account['email'], account['password'], recipient,
                  "Warm-Up Email", "This is a warm-up email to improve reputation."),
            trigger="interval",
            seconds=interval,
            max_instances=10  # Prevent overlapping jobs
        )


# Send an email
def send_email(smtp_server, port, email, password, to_email, subject, body):
    success = False
    try:
        # Email sending logic (existing code)
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(email, password)

        message = MIMEMultipart()
        message['From'] = email
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        server.sendmail(email, to_email, message.as_string())
        server.quit()

        success = True
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

    # Update analytics
    for account in analytics:
        if account['email'] == email:
            if success:
                account['sent'] += 1
            else:
                account['spam'] += 1
    return success

# Update analytics
def update_analytics(email, action):
    for account in analytics:
        if account['email'] == email:
            if action == "sent":
                account['sent'] += 1
            elif action == "spam":
                account['spam'] += 1
            elif action == "replies":
                account['replies'] += 1

if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=5000)
