# Rancher の立ち上げと使用方法

このディレクトリには、Rancherをdocker-composeで立ち上げるための設定ファイルが含まれています。以下の手順に従って、Rancherを立ち上げ使用してください。

## 前提条件

- Dockerがインストールされていること
- docker-composeがインストールされていること

## Rancherの立ち上げ方法

1. このディレクトリ内で以下のコマンドを実行し、Rancherを立ち上げます。

   ```
   cd src/rancher
   docker-compose up --build
   ```

2. Rancherが正常に立ち上がったことを確認するため、以下のコマンドを実行します。

   ```
   docker-compose ps
   ```

   `rancher` サービスが `running` 状態になっていれば成功です。

3. ブラウザから `http://localhost` にアクセスし、Rancherの管理画面を開きます。

## Rancherの初期設定

1. 管理画面が表示されたら、初期パスワードを設定します。

2. Rancherのサーバー URL を設定します。ローカル環境で立ち上げた場合は `http://localhost` を指定してください。

3. Rancherで管理するクラスターを追加します。「Add Cluster」ボタンをクリックし、クラスター名を入力後、「Create」をクリックします。

4. クラスターが作成されたら、そのクラスターを選択し、ダッシュボードを開きます。

これで、Rancherの立ち上げと初期設定が完了です。Rancherの詳しい使い方については、公式ドキュメントを参照してください。

## Rancherの停止方法

Rancherを停止するには、以下のコマンドを実行します。

```
docker-compose down
```

これにより、Rancherのサービスが停止します。再度立ち上げる場合は、`docker-compose up -d` コマンドを実行してください。