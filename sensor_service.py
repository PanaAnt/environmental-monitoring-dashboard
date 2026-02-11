import os
from dotenv import load_dotenv
import time
import json
import redis
import datetime
import smtplib
from sensor_logic.sensor import AHT20sensor

load_dotenv()

#smtp configuration
SMTP_PORT = 587
SMTP_SERVER = os.getenv("SMTP_SERVER") # SMTP_SERVER = e.g. "smtp.gmail.com"
SENDER_EMAIL = os.getenv("SENDER_EMAIL") # SENDER_EMAIL=your_email@email.com
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") # SENDER_PASSWORD=your_email_app_password
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL") # RECEIVER_EMAIL=alert_recipient@email.com

temp_min = 17.0
temp_max = 26.0
alert_cooldown = 180 
previous_alert = 0


def send_alert(temperature):
    """send email alert if temp and humidity are outside threshold"""
    if temperature > temp_max:
        subject = "Temperature WARNING: Too hot!"
        message = f"Temperature is {temperature:.2f} Celsius, MAX TEMP: {temp_max} Celsius."
    else:
        subject = "Temperature WARNING: Too cold!"
        message = f"Temperature is {temperature:.2f} Celsius, MIN TEMP: {temp_min} Celsius."
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, f"Subject: {subject}\n\n{message}")
        server.quit()
        print(f"Alert sent: {subject}")

    except Exception as e:
        print(f"Failed to connect to SMTP server: {e}")

def check_alert(temperature):
    """Check if temperature is outside threshold and send alert if cooldown period expired"""
    global previous_alert
    if temperature < temp_min or temperature > temp_max:
        current_time = time.time()
        if current_time - previous_alert >= alert_cooldown:
            send_alert(temperature)
            previous_alert = current_time


# Redis client
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Sensor
sensor = AHT20sensor(interval=2.0)
sensor.start()

print("Sensor service running. Press Ctrl+C to stop.\n")
print(f"Monitoring temperature ({temp_min}°C - {temp_max}°C)")
print(f"Alerts to: {RECEIVER_EMAIL}\n")

try:
    while True:
        data = sensor.get_latest()
        if data is None:
            time.sleep(2)
            continue

        payload = {
            "temperature": data["temperature"],
            "humidity": data["humidity"],
            "timestamp": time.time(),
            "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Store latest and timestamp 
        r.set("sensor:latest", json.dumps(payload))
        r.set("sensor:timestamp", payload["timestamp"])

        # Push into rolling window (max 5 readings)
        r.lpush("sensor:history", json.dumps(payload))
        r.ltrim("sensor:history", 0, 4)

        check_alert(temperature=data["temperature"])

        time.sleep(2)

except KeyboardInterrupt:
    print("\nShutting down sensor service...")

finally:
    # Stop sensor thread
    sensor.stop()

    # Delete ALL Redis keys
    r.flushdb()

    # Close Redis connection
    r.close()
    
    print("Sensor stopped. Redis cleaned. Exiting.")
