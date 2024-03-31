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

# インストール方法
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