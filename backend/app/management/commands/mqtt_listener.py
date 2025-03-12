from django.core.management.base import BaseCommand
import os
import paho.mqtt.client as mqtt
import requests

class Command(BaseCommand):
    help = "Starts the MQTT client to listen for QR code scans"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting MQTT client...")

        # Load MQTT settings from environment variables
        MQTT_BROKER = os.getenv("MQTT_BROKER_URL", "mqtt.eclipseprojects.io")
        MQTT_PORT = int(os.getenv("MQTT_BROKER_PORT", 1883))
        MQTT_TOPIC = "warehouse/qr"
        BACKEND_URL = "https://smartchainerp2.onrender.com/api/store_qr/"  # Updated URL

        # Define MQTT callbacks
        def on_connect(client, userdata, flags, rc):
            self.stdout.write(f"Connected to MQTT with result code {rc}")
            client.subscribe(MQTT_TOPIC)

        def on_message(client, userdata, msg):
            data = msg.payload.decode()
            self.stdout.write(f"Received QR data: {data}")

            # Send HTTP POST request to backend
            try:
                response = requests.post(BACKEND_URL, json={"qr_text": data})  # Ensure the key is 'qr_text'
                if response.status_code == 200:
                    self.stdout.write(f"[✅] QR Data sent to backend: {response.json()}")
                else:
                    self.stdout.write(f"[❌] Failed to send QR data. Status: {response.status_code}")
                    self.stdout.write(f"Response content: {response.content}")
            except requests.RequestException as e:
                self.stdout.write(f"[⚠] Error sending QR data via HTTP: {e}")

        # Set up MQTT client (No username or password)
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = on_connect
        mqtt_client.on_message = on_message

        # Connect to MQTT broker
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

        self.stdout.write("MQTT client started, waiting for messages...")
        mqtt_client.loop_forever()  # Keeps the process running