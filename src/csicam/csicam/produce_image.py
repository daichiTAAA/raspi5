import sys
import time
import socket
from datetime import datetime
from io import BytesIO

sys.path.append("/usr/lib/python3/dist-packages")
print(sys.path)

from picamera2 import Picamera2, Preview
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


def delivery_report(err, msg):
    if err is not None:
        print("Message delivery failed: {}".format(err))
    else:
        print("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))


# Kafka設定
bootstrap_servers = "192.168.0.104:9092"
topic = "image-data"

# Schema Registry設定
schema_registry_url = "http://192.168.0.104:8081"
schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})

# スキーマ定義
schema_str = """
{
   "namespace": "csicam.image",
   "name": "Value",
   "type": "record",
   "fields" : [
     {
       "name" : "image",
       "type" : "bytes"
     },
     {
       "name" : "timestamp",
       "type" : "string"
     },
     {
       "name" : "ip_address",
       "type" : "string"
     }
   ]
}
"""

avro_serializer = AvroSerializer(schema_registry_client, schema_str)

producer_conf = {"bootstrap.servers": bootstrap_servers}
producer = Producer(producer_conf)

with Picamera2(0) as picam2:
    picam2.start_preview(Preview.NULL)

    while True:
        img_buffer = BytesIO()
        picam2.start_and_capture_file(img_buffer)
        img_bytes = img_buffer.getvalue()

        timestamp = datetime.now().isoformat()
        ip_address = socket.gethostbyname(socket.gethostname())

        # メッセージ作成
        message = {"image": img_bytes, "timestamp": timestamp, "ip_address": ip_address}

        # シリアライズ
        producer.produce(
            topic=topic,
            value=avro_serializer(message, schema_str),
            callback=delivery_report,
        )

        producer.flush()

        picam2.stop()
        time.sleep(1)
