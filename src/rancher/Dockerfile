# FROM rancher/rancher:latest

# # Rancherディレクトリの作成
# RUN mkdir -p /etc/rancher/rke2

# # config.yamlの作成
# RUN echo "token: mylittlepony" > /etc/rancher/rke2/config.yaml && \
#     echo "tls-san:" >> /etc/rancher/rke2/config.yaml && \
#     echo "  - 192.168.0.102" >> /etc/rancher/rke2/config.yaml

# # デフォルトのコマンド  
# CMD ["rancher", "--http-listen-port=80", "--https-listen-port=443"]

# Dockerfileのベースイメージとして、ARM64アーキテクチャをサポートするUbuntuを使用します。
FROM ubuntu:latest

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    curl \
    nano \
    sudo

# Rancherのインストールスクリプトを実行するための環境設定
RUN mkdir -p /etc/rancher/rke2 \
    && echo "token: mylittlepony" > /etc/rancher/rke2/config.yaml \
    && echo "tls-san:" >> /etc/rancher/rke2/config.yaml \
    && echo "  - 192.168.0.102" >> /etc/rancher/rke2/config.yaml

# Rancherをインストール
RUN curl -sfL https://get.rancher.io | sh -

# コンテナ起動時にRancherサーバーを起動する
CMD ["rancher", "server", "start"]