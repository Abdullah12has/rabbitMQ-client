import json
import pika
import ssl
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

host = "86.50.253.233"
port = 5672
vhost = "AMUMMM-vhost"
username = "AMUMMM"
password = "zB-1wNrWWZJUlK03Uo_3_GZOYyUNOQ7k4l7X9NychIA"

# Set up SSL context using your cert and key
context = ssl.create_default_context()
context.load_cert_chain(certfile="./AMUMMM.crt", keyfile="./client.key")
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE  # Use CERT_REQUIRED if you have the CA cert

# Set up RabbitMQ connection parameters with SSL
credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(
    host=host,
    port=port,
    virtual_host=vhost,
    credentials=credentials,
    ssl_options=pika.SSLOptions(context, host)
)

def notification_handler(ch, method, properties, body):
    """Callback to handle incoming notifications"""
    try:
        data = json.loads(body)
        logging.info(f"📥 Received message: {json.dumps(data, indent=2)}")

    except (KeyError, json.JSONDecodeError) as e:
        logging.error(f"Error processing message: {e}")
    else:
        logging.info(f"Message processed successfully.")

def listen_notifications():
    """Listen for notifications on the RabbitMQ exchange"""
    try:
        # Establish connection to RabbitMQ
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        logging.info(f"Connected to RabbitMQ at {host}:{port}, vhost: {vhost}")

        # Declare exchange and queue for notifications
        channel.exchange_declare(
            exchange="notifications",
            exchange_type="fanout"  # Assuming fanout for broadcasting messages
        )
        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue
        logging.info(f"Created temporary queue: {queue_name}")

        # Bind the queue to the exchange
        channel.queue_bind(
            exchange="notifications",
            queue=queue_name
        )
        logging.info("Queue bound to 'notifications' exchange.")

        # Listen for messages from the queue
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=notification_handler,
            auto_ack=True
        )

        logging.info("🔔 Listening for notifications...")
        channel.start_consuming()

    except Exception as e:
        logging.error(f"Error connecting or consuming messages: {e}")

if __name__ == "__main__":
    listen_notifications()
