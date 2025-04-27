import json
import requests
import pika
import urllib3
import ssl

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GROUP = "AMUMMM"
RABBIT_KEY = "zB-1wNrWWZJUlK03Uo_3_GZOYyUNOQ7k4l7X9NychIA"
API_KEY = "iZe7EB9WTHrGpac0RfbRnrdXvHNRIPJ9shcJw3EMLv4"
API_BASE = "https://193.167.189.95/api/"

HEADERS = {
    "Pwp-Api-Key": API_KEY
}

def listen_for_certificate():
    host = "86.50.253.233"
    port = 5672
    vhost = "AMUMMM-vhost"
    username = "AMUMMM"
    password = RABBIT_KEY
    exchange_name = "notifications"

    print(" Connecting to RabbitMQ with TLS and client certs...")

    context = ssl.create_default_context(cafile="pwp-ca.crt")
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_cert_chain(
        certfile="AMUMMM.crt",
        keyfile="client.key"
    )

    credentials = pika.PlainCredentials(username, password)

    connection_params = pika.ConnectionParameters(
        host=host,
        port=port,
        virtual_host=vhost,
        credentials=credentials,
        ssl_options=pika.SSLOptions(context, host)
    )

    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange_name, queue=queue_name)

    print(f" Waiting for a certificate notification on queue: {queue_name}")

    def callback(ch, method, properties, body):
        print(" Notification received!")
        data = json.loads(body)
        print(data)
        try:
            href = data["@controls"]["pwpex:get-certificate"]["href"]
            print(f" Downloading certificate from {href}")
            download_certificate(href)
        except (KeyError, TypeError) as e:
            print("Failed to extract certificate link:", e)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def download_certificate(href):
    res = requests.get(href, headers=HEADERS, verify=False)
    res.raise_for_status()
    cert = res.json()
    with open("certificate.json", "w") as f:
        json.dump(cert, f, indent=2)
    print(" Certificate saved to certificate.json")

def main():
    print(" Fetching API entry point...")
    res = requests.get(API_BASE, headers=HEADERS, verify=False)
    res.raise_for_status()
    print(res.json())

    print("Fetching AMUMMM group info...")
    res = requests.get(f"{API_BASE}groups/{GROUP}/", headers=HEADERS, verify=False)
    res.raise_for_status()
    print(res.json())

    print("Fetching AMUMMM group certificates...")
    res = requests.get(f"{API_BASE}groups/{GROUP}/certificates/", headers=HEADERS, verify=False)
    res.raise_for_status()
    print(res.json())

    print("Requesting a new certificate...")
    res = requests.post(f"{API_BASE}groups/{GROUP}/certificates/", headers=HEADERS, verify=False)
    res.raise_for_status()
    print(res.status_code)

    print("Verifying certificate request...")
    res = requests.get(f"{API_BASE}groups/{GROUP}/certificates/", headers=HEADERS, verify=False)
    res.raise_for_status()
    print(res.json())

    listen_for_certificate()

if __name__ == "__main__":
    main()
