# 調査資料 - Rancherの調査
&nbsp;
# 作成記録
---
* 作成日時 2024/3/31 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはRancherの調査結果の資料である。
&nbsp;
# 対象読者
---
* このドキュメントはRancherの調査結果を確認したいエンジニア用である。
&nbsp;
# 目的
---
* Rancherの調査結果を記載する。
&nbsp;

# 内容
---
# Rancherとは
Rancherは、Kubernetesクラスターの管理を簡素化するためのオープンソースのプラットフォームです。以下のような特徴があります。

- 複数のKubernetesクラスターを一元的に管理できる
  - クラスターのプロビジョニング、デプロイ、モニタリングなどの作業を効率的に行える
- 直感的に操作できるWebベースのユーザーインターフェースを提供
  - Kubernetesの知識がなくても、GUIから簡単にクラスターを管理できる
- Kubernetesリソースの管理やアプリケーションのデプロイが可能
  - ワークロードの管理、ロードバランサーの設定、ストレージの管理などをGUIから行える
- マルチクラウド、マルチクラスターの管理に対応
  - オンプレミス、パブリッククラウドなど、様々な環境で動作するKubernetesクラスターを一元管理できる
- オープンソースで、コミュニティによって活発に開発されている
  - 商用サポートを提供するRancher Labsがバックアップしており、エンタープライズでの利用にも適している

以上のように、Rancherは、Kubernetesクラスターの管理やアプリケーションデプロイの効率化を実現するための強力なプラットフォームです。

# 参考
- [Rancher](https://www.rancher.com/)
- [Rancher Labs](https://www.rancher.com/products/rancher-labs/)

# インストール方法(ARM64では不可)
- 参考: https://www.youtube.com/watch?v=X9fSMGkjtug
- 参考: https://ranchermanager.docs.rancher.com/getting-started/quick-start-guides/deploy-rancher-manager/helm-cli
- k3sを動かしている以外のPCやVM、WSL2にインストールする
- config.yamlの作成
  ```bash
  sudo mkdir /etc/rancher
  sudo mkdir /etc/rancher/rke2
  cd /etc/rancher/rke2
  sudo nano config.yaml
  ```
  下記の内容をconfig.yamlに書き込む。
  ```
  token: {トークン}
  tls-san:
    - {k3sマスターノードのIPアドレス}
  ```
記載例：
```
token: mylittlepony
tls-san:
  - 192.168.0.102
```
- Rancherをインストールする
  ```bash
  curl -sfL https://get.rancher.io | sh -
  ```
  次のエラーが出る場合は、`[ERROR] You need to be root to perform this install`　root ユーザーに切り替えてからスクリプトを実行する
  ```bash
  sudo su -
  curl -sfL https://get.rancher.io | sh -
  ```
  インストールが完了したら`exit`でrootユーザーを抜ける

- Rancherのヘルプの確認方法
  ```bash
  rancherd --help
  ```
- Rancherの起動方法
  ```bash
  cd /etc/rancher/rke2
  sudo systemctl enable rancherd-server.service
  sudo systemctl start rancherd-server.service
  sudo journalctl -eu rancherd-server -f
  ```

# アカウントの取得とアクセス方法
  ```bash
  sudo rancherd reset-admin
  ```
  コンソールにServer URL、Username、Passwordが表示されるためそれらを使用してアクセスする。

# systemctl で正しく終了しなかったためにエラーが出る場合の対処方法
systemctl で正しく終了しなかったためにエラーが出る場合は、以下の手順を試してみてください。

1. 実行中のプロセスを強制終了する:
   ```bash
   sudo systemctl kill <service_name>
   ```
   `<service_name>` を実際のサービス名に置き換えてください。
  - Rancherを再度インストールする
    ```bash
    curl -sfL https://get.rancher.io | sh -
    ```
    次のエラーが出る場合は、`[ERROR] You need to be root to perform this install`　root ユーザーに切り替えてからスクリプトを実行する
    ```bash
    sudo su -
    curl -sfL https://get.rancher.io | sh -
    ```

2. サービスを再起動する:
   ```bash
   sudo systemctl restart <service_name>
   ```
   これにより、サービスが正しく終了され、再起動されます。

3. サービスのステータスを確認する:
   ```bash
   sudo systemctl status <service_name>
   ```
   これにより、サービスが正常に動作しているかどうかを確認できます。

4. サービスを停止する:
   ```bash
   sudo systemctl stop <service_name>
   ```
   これにより、サービスを正常に停止できます。

5. サービスを無効にする:
   ```bash
   sudo systemctl disable <service_name>
   ```
   これにより、システムの起動時にサービスが自動的に起動しないようにできます。

6. サービスを有効にする:
   ```bash
   sudo systemctl enable <service_name>
   ```
   これにより、システムの起動時にサービスが自動的に起動するようにできます。

これらの手順を試しても問題が解決しない場合は、以下の追加の手順を試してみてください。

1. ログファイルを確認する:
   ```bash
   sudo journalctl -u <service_name>
   ```
   これにより、サービスに関連するログメッセージを表示できます。エラーの原因を特定するのに役立つ情報が含まれている可能性があります。

2. サービスの設定ファイルを確認する:
   サービスの設定ファイルに誤りがある可能性があります。設定ファイルの場所はサービスによって異なりますが、通常は `/etc/` ディレクトリ内にあります。設定ファイルを確認し、必要に応じて修正してください。

これらの手順を実行しても問題が解決しない場合は、システム管理者またはサービスのドキュメントを参照して、さらなるトラブルシューティングの手順を確認することをお勧めします。