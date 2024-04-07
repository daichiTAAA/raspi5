# AKHQ Docker Compose

このディレクトリには、AKHQをDockerコンテナで実行するための`docker-compose.yaml`ファイルが含まれています。

## 前提条件

- Dockerがインストールされていること
- docker-composeがインストールされていること

## 使用方法

1. `docker-compose.yaml`ファイルを編集し、以下の環境変数を設定してください：
   - `bootstrap.servers`: Kafkaブローカーのホスト名またはIPアドレスとポート番号
   - `schema-registry.url`: Schema Registryのホスト名またはIPアドレスとポート番号

2. ターミナルでこのディレクトリに移動し、以下のコマンドを実行してAKHQを起動します：

   ```
   cd src/akhq
   docker compose up
   ```

3. ブラウザで`http://localhost:8080`にアクセスし、AKHQのWebインターフェースを開きます。

4. AKHQを停止するには、以下のコマンドを実行します：

   ```
   docker compose down
   ```

## 設定

`docker-compose.yaml`ファイルでは、以下の設定が可能です：

- `ports`: AKHQのWebインターフェースのポート番号を指定します。デフォルトは`8080`です。
- `environment`: AKHQの設定を環境変数で指定します。`AKHQ_CONFIGURATION`変数にYAML形式の設定を記述します。

詳細な設定方法については、AKHQの公式ドキュメントを参照してください。