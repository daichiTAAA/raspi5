# 調査資料 - Dockerの初期設定方法
&nbsp;
# 作成記録
---
* 作成日時 2024/3/15 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはDockerの初期設定方法の調査資料である。
&nbsp;
# 対象読者
---
* このドキュメントはDockerの初期設定方法を確認したいエンジニア用である。
&nbsp;
# 目的
---
* Dockerの初期設定方法を記載する。
&nbsp;

# 内容
---
# インストール方法
* 下記の記事を参考にDocker Engineをインストールする
  - https://docs.docker.com/engine/install/ubuntu/
    ```bash
    # Add Docker's official GPG key:
    sudo apt-get update
    sudo apt-get install ca-certificates curl
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc

    # Add the repository to Apt sources:
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    ```

    To install the latest version, run:
    ```bash
    sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    ```

    Verify that the Docker Engine installation is successful by running the hello-world image.
    ```bash
    sudo docker run hello-world
    ```

* 下記のホームページを参考にその他の設定を行う
  - https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user
    - sudoコマンド無しでdockerコマンドを実行できるようにする
      ```bash
      sudo groupadd docker
      sudo usermod -aG docker $USER
      newgrp docker
      ```
    - システム起動時のDocker自動起動設定を行う
      ```bash
      sudo systemctl enable docker.service
      sudo systemctl enable containerd.service
      ```