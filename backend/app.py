import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
CORS(app)

# In-memory storage (replace with a database later)
accounts = []
analytics = []

# Scheduler for sending emails
scheduler = BackgroundScheduler()
scheduler.start()

def send_email(email, password, to_email, subject, body, smtp_server, port):
    try:
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
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def schedule_emails(email_account, emails_per_day, warmup_rate):
    # Spread emails evenly over the day
    interval_seconds = 86400 // emails_per_day

    for i in range(emails_per_day):
        scheduler.add_job(
            func=send_email,
            args=(
                email_account['email'],
                email_account['password'],
                "scamp121206@gmail.com",
                "Warm-Up Email",
                "This is an automated warm-up email.",
                email_account['smtp_server'],
                email_account['port']
            ),
            trigger="interval",
            seconds=interval_seconds,
            id=f"{email_account['email']}_email_{i}",
            replace_existing=True
        )

@app.route('/add_account', methods=['POST'])
def add_account():
    data = request.json
    email = data.get('email')
    provider = data.get('provider')
    password = data.get('password')  # Add password field
    smtp_server = data.get('smtp_server')
    port = data.get('port')

    if email and provider and password and smtp_server and port:
        account = {
            'email': email,
            'provider': provider,
            'password': password,
            'smtp_server': smtp_server,
            'port': port
        }
        accounts.append(account)
        analytics.append({'email': email, 'delivery_rate': 100, 'spam_rate': 0, 'engagement_rate': 0})
        return jsonify({'message': 'Account added successfully!'}), 201
    return jsonify({'message': 'Invalid input!'}), 400

@app.route('/set_schedule', methods=['POST'])
def set_schedule():
    data = request.json
    email = data.get('email')
    emails_per_day = data.get('emails_per_day')
    warmup_rate = data.get('warmup_rate')

    email_account = next((acc for acc in accounts if acc['email'] == email), None)

    if email_account and emails_per_day and warmup_rate:
        schedule_emails(email_account, int(emails_per_day), warmup_rate)
        return jsonify({'message': 'Warm-up schedule set successfully!'}), 200
    return jsonify({'message': 'Invalid input or account does not exist!'}), 404

@app.route('/analytics', methods=['GET'])
def get_analytics():
    return jsonify(analytics), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
