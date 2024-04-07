import os
from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

# Kafka設定
bootstrap_servers = "192.168.0.104:9092"
topic = "image-data"
group_id = "image-consumer-group"

# Schema Registry設定
schema_registry_url = "http://192.168.0.104:8081"
schema_registry_client = SchemaRegistryClient({"url": schema_registry_url})

subject_name = f"{topic}-value"
avro_deserializer = AvroDeserializer(schema_registry_client, None, subject_name)

consumer_conf = {
    "bootstrap.servers": bootstrap_servers,
    "group.id": group_id,
    "auto.offset.reset": "earliest",
}

consumer = Consumer(consumer_conf)
consumer.subscribe([topic])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        # メッセージをデシリアライズ
        deserialized_message = avro_deserializer(msg.value(), None)

        timestamp = deserialized_message["timestamp"]
        image_bytes = deserialized_message["image"]

        # 画像をJPGファイルとして保存
        output_dir = "received_images"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{timestamp}.jpg")
        with open(output_path, "wb") as f:
            f.write(image_bytes)

        print(f"Image saved: {output_path}")

except KeyboardInterrupt:
    pass

finally:
    consumer.close()
