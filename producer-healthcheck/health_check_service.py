from flask import Flask, jsonify
from confluent_kafka import Consumer, KafkaException, KafkaError, Producer
import threading
import logging
import os
import time
import requests
import json
from datetime import datetime, timezone

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Environment variables configuration
kafka_broker = os.getenv('KAFKA_BROKER', 'my-kafka:9092')
kafka_topic = os.getenv('KAFKA_TOPIC', 'health_checks_topic')
service_url = os.getenv('SERVICE_URL', 'http://my-service:80')

logger.info(f'Kafka broker: {kafka_broker}')
logger.info(f'Kafka topic: {kafka_topic}')
logger.info(f'Service URL: {service_url}')

# Consumer configuration, credentials should ideally be stored in a secure location
kafka_config = {
    'bootstrap.servers': kafka_broker,
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'user1',
    'sasl.password': 'vgJSL9Uh6Y'
}

consumer_config = kafka_config.copy()
consumer_config.update({
    'group.id': 'health-check-service-group',
    'auto.offset.reset': 'earliest',
})

producer = Producer(kafka_config)

# Health check service
def health_check_service():
    try:
        response = requests.get(service_url)
        if response.status_code == 200:
            status = "OK"
        else:
            status = "FAIL"
    except requests.exceptions.RequestException as e:
        logger.error(f'Error checking {service_url}: {e}')
        status = "ERROR"
    
    health_check_result = {
        "service_name": "my-service",
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # Produce the result to Kafka topic
    producer.produce(kafka_topic, key="health_check", value=json.dumps(health_check_result))
    producer.flush()
    
    logger.info(f'Produced health check result: {health_check_result}')
    return health_check_result

# Check health endpoint implementation
def health_check_service_loop():
    while True:
        health_check_service()
        time.sleep(3)

def consume_health_checks():
    logger.info('Consumer thread started')
    consumer = Consumer(consumer_config)
    consumer.subscribe([kafka_topic])
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                logger.error(f'Kafka error: {msg.error()}')
                continue

        health_check = json.loads(msg.value().decode('utf-8'))
        logger.info(f'Received health check: {health_check}')

@app.route('/check_health', methods=['GET'])
def check_health():
    logger.info('check_health endpoint called')
    health_check_result = health_check_service()
    return jsonify(health_check_result)

def start_consumer_thread():
    logger.info('Starting consumer thread')
    thread = threading.Thread(target=consume_health_checks)
    thread.daemon = True
    thread.start()

def start_health_check_thread():
    logger.info('Starting health check service loop')
    thread = threading.Thread(target=health_check_service_loop)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    start_consumer_thread()  # Start the consumer thread
    start_health_check_thread()  # Start the health check service loop thread
    app.run(host='0.0.0.0', port=5001)
