from django.core.management.base import BaseCommand
import os
import time
import paho.mqtt.client as mqtt
import requests
import logging

# Configure logging
logging.basicConfig(filename="mqtt_listener.log", level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger()

class Command(BaseCommand):
    help = "Starts the MQTT client to listen for QR code scans"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting MQTT client...")

        # Load MQTT settings from environment variables
        MQTT_BROKER = os.getenv("MQTT_BROKER_URL", "broker.hivemq.com")
        MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
        MQTT_TOPIC = "warehouse/qr"
        BACKEND_URL = "https://smartchainerp2.onrender.com/api/store_qr/"

        def send_qr_data(qr_text):
            """Send QR data to Django backend with retry logic"""
            max_retries = 5
            retry_delay = 3  # seconds

            for attempt in range(max_retries):
                try:
                    response = requests.post(BACKEND_URL, json={"qr_text": qr_text})
                    if response.status_code == 200:
                        logger.info(f"[✅] QR Data sent: {response.json()}")
                        return
                    else:
                        logger.warning(f"[❌] Failed to send QR data. Status: {response.status_code}, Attempt {attempt + 1}")
                except requests.RequestException as e:
                    logger.error(f"[⚠] Request error: {e}, Retrying... ({attempt + 1}/{max_retries})")
                time.sleep(retry_delay)

            logger.error(f"[🚨] Failed to send QR data after {max_retries} attempts.")

        def on_connect(client, userdata, flags, rc):
            logger.info(f"Connected to MQTT with result code {rc}")
            client.subscribe(MQTT_TOPIC)

        def on_message(client, userdata, msg):
            data = msg.payload.decode()
            logger.info(f"Received QR data: {data}")
            send_qr_data(data)

        def on_disconnect(client, userdata, rc):
            logger.warning(f"[⚠] Disconnected from MQTT broker. Reconnecting...")
            while True:
                try:
                    client.reconnect()
                    logger.info("[✅] Reconnected to MQTT broker!")
                    return
                except:
                    time.sleep(5)

        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message
        mqtt_client.on_disconnect = on_disconnect

        # Connect to MQTT broker
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

        self.stdout.write("MQTT client started, waiting for messages...")
        mqtt_client.loop_forever()
