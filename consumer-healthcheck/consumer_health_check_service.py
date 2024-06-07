from flask import Flask, jsonify
from confluent_kafka import Consumer, KafkaException, KafkaError
import threading
import logging
import os
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables configuration
kafka_broker = os.getenv('KAFKA_BROKER', 'my-kafka:9092')
kafka_topic = os.getenv('KAFKA_TOPIC', 'health_checks_topic')

logger.info(f'Kafka broker: {kafka_broker}')
logger.info(f'Kafka topic: {kafka_topic}')

# Consumer configuration, credentials should ideally be stored in a secure location
consumer_config = {
    'bootstrap.servers': kafka_broker,
    'group.id': 'consumer-health-check-service-group',
    'auto.offset.reset': 'earliest',
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'user1',
    'sasl.password': 'vgJSL9Uh6Y'
}

latest_health_check = None

def consume_health_checks():
    global latest_health_check
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
        latest_health_check = health_check
        logger.info(f'Received health check: {health_check}')

@app.route('/get_latest_health_check', methods=['GET'])
def get_latest_health_check():
    if latest_health_check is not None:
        logger.info(f'Latest health check: {latest_health_check}')
        return jsonify(latest_health_check)
    else:
        return jsonify({"message": "No health check data available"}), 404

def start_consumer_thread():
    logger.info('Starting consumer thread')
    thread = threading.Thread(target=consume_health_checks)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    start_consumer_thread()  # Start the consumer thread
    app.run(host='0.0.0.0', port=5001)
