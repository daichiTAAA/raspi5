# send_image_left_csicam

このフォルダには、Raspberry PiのCSIカメラから画像を取得し、Kafkaトピックに送信するPythonスクリプトとDockerファイルが含まれています。

# 使用方法

1. docker-compose.yamlファイルがあるディレクトリで以下のコマンドを実行し、Dockerイメージをビルドします。

   ```
   cd src/kafka_from_csicam/send_image_left_csicam
   docker compose build
   ```

2. 次のコマンドでDockerコンテナを起動します。

   ```
   cd src/kafka_from_csicam/send_image_left_csicam
   docker compose up
   ```

   これにより、CSIカメラから画像が取得され、Kafkaトピック`image-data-left-csicam`に送信されます。

3. コンテナを停止するには、以下のコマンドを実行します。

   ```
   cd src/kafka_from_csicam/send_image_left_csicam
   docker compose down
   ```

# 設定

- Kafkaブローカーのアドレスとトピック名は、`produce_image.py`の`bootstrap_servers`と`topic`変数で設定できます。
- Schema Registryのアドレスは、`produce_image.py`の`schema_registry_url`変数で設定できます。