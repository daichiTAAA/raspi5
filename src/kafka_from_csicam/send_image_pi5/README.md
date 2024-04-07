# send_image_left_csicam

このフォルダには、Raspberry PiのCSIカメラから画像を取得し、Kafkaトピックに送信するPythonスクリプトとDockerファイルが含まれています。

# 使用方法

1. docker-compose.yamlファイルがあるディレクトリで以下のコマンドを実行し、Dockerイメージをビルドします。

   ```
   cd src/kafka_from_csicam/send_image_left_csicam
   sudo docker compose build
   ```

2. 次のコマンドでDockerコンテナを起動します。

   ```
   cd src/kafka_from_csicam/send_image_left_csicam
   sudo docker compose up
   ```

   ビルドと実行を同時にする場合は下記のコードを実行します。
   ```
   cd src/kafka_from_csicam/send_image_left_csicam
   sudo docker compose up --build
   ```

   これにより、CSIカメラから画像が取得され、Kafkaトピック`image-data-left-csicam`に送信されます。

3. コンテナを停止するには、以下のコマンドを実行します。

   ```
   cd src/kafka_from_csicam/send_image_left_csicam
   sudo docker compose down
   ```

# 設定

- Kafkaブローカーのアドレスとトピック名は、`produce_image.py`の`bootstrap_servers`と`topic`変数で設定できます。
- Schema Registryのアドレスは、`produce_image.py`の`schema_registry_url`変数で設定できます。

# tlsエラー時の対応方法
* 下記のエラーが出た場合、下記のコマンドを実行する。
  * `tls: failed to verify certificate: x509: certificate has expired or is not yet valid: current time`
```bash
sudo apt update
sudo apt install ntpdate
sudo ntpdate ntp.nict.jp
```
