# Kafka と Schema Registry の実行方法

このリポジトリには、Kafka と Schema Registry を Docker Compose で実行するための設定ファイルが含まれています。

## 前提条件

- Docker と Docker Compose がインストールされていること

## 実行手順

1. Dockerネットワークを作成します。
    ```bash
    sudo docker network create kafka-net
    ```

2. 以下のコマンドを実行して、Kafka と Schema Registry を起動します。

   ```bash
   cd src/kafka
   sudo docker compose up
   ```

3. Kafka と Schema Registry が正常に起動したことを確認するには、以下のコマンドを実行します。

   ```bash
   sudo docker compose ps
   ```

   `broker` と `schema-registry` のコンテナが `Up` 状態になっていれば OK です。

4. Kafka と Schema Registry を停止するには、以下のコマンドを実行します。

   ```bash
   sudo docker compose down
   ```

以上で、Kafka と Schema Registry を実行できます。設定の詳細については、`docker-compose.yaml` ファイルを参照してください。