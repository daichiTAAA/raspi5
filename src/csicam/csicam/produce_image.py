import sys
import time
import socket
from datetime import datetime
from io import BytesIO
import tempfile

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
     },
     {
       "name" : "image_size",
       "type" : "int"
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
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_file:
            picam2.start_and_capture_file(temp_file.name)

            # 一時ファイルから画像データを読み込む
            temp_file.seek(0)
            img_bytes = temp_file.read()
            img_size = len(img_bytes)

            timestamp = datetime.now().isoformat()
            ip_address = socket.gethostbyname(socket.gethostname())

            # メッセージ作成
            message = {
                "image": img_bytes,
                "timestamp": timestamp,
                "ip_address": ip_address,
                "image_size": img_size,  # 画像サイズ（バイト単位）
            }

            # シリアライズ
            producer.produce(
                topic=topic,
                value=avro_serializer(message, ctx=None),
                callback=delivery_report,
            )

            producer.flush()

        time.sleep(1)
