# 調査資料 - RaspberryPi5の初期設定方法
&nbsp;
# 作成記録
---
* 作成日時 2024/3/15 野田大一郎
* 更新日時 2024/4/7 野田大一郎
&nbsp;
# 概要
---
* このドキュメントはRaspberryPi5の初期設定方法の調査資料である。
&nbsp;
# 対象読者
---
* このドキュメントはRaspberryPi5の初期設定方法を確認したいエンジニア用である。
&nbsp;
# 目的
---
* RaspberryPi5の初期設定方法を記載する。
&nbsp;

# 内容
---
# 初期設定方法
* 下記の記事を参考に~~Ubuntu Server 23.10 (64-bit)をインストールする~~<br>
  Raspberry Pi OS Lite(64-bit)をインストールする。RaspiCameraモジュールを使用しやすいようにするため。
  - https://tks2.co.jp/2024/02/18/raspberry-pi-5-%E3%81%AB-ubuntu-server-%E3%82%92%E7%B0%A1%E5%8D%98%E3%82%BB%E3%83%83%E3%83%88%E3%82%A2%E3%83%83%E3%83%97/
* VS CodeのDev Continerを使用してからWifi経由でSSHでアクセスする

&nbsp;

# SSDでの起動方法
* 下記の記事を参考にする
  * https://zenn.dev/usagi1975/articles/2023-12-29-000_raspi5_boot_nvme

&nbsp;

# SSH接続できない場合の対象方法
### OSを再インストールした場合など
* SSH接続先のホスト名の古いSSHキーがSSH接続元PC側に残っているとエラーとなる
* SSH接続元PCの/{user}/.ssh/known_hostsファイル中のSSH接続先のホスト名の古いSSHキーを削除する

&nbsp;

# IPアドレスの固定
Linuxシステムでは、ネットワークインターフェースの設定ファイルを編集することでIPアドレスを固定できます。具体的な手順は以下の通りです。

1. ネットワークインターフェースの設定ファイルを開きます。
   - Debianベースのシステム（Raspberry Pi OSを含む）では、`/etc/network/interfaces`ファイルを編集します。

     ```bash
     sudo nano /etc/network/interfaces
     ```

2. 以下のような設定を追加します。これらの値は実際の環境に合わせて変更してください。元の行の下に行を追加して追加します。
```
auto {ネットワークインターフェース名}
iface {ネットワークインターフェース名} inet static
    address {固定したいIPアドレス}
    netmask {サブネットマスク}
    gateway {ゲートウェイのIPアドレス}
    dns-nameservers {DNSサーバーのIPアドレス}
```

例：
```
auto eth0
iface eth0 inet static
    address 192.168.0.10
    netmask 255.255.255.0
    gateway 192.168.0.1
    dns-nameservers 192.168.0.1
```

3. 設定ファイルを保存し、エディタを終了します。

4. 変更を適用するために、ネットワークサービスを再起動します。

   ```bash
   sudo systemctl restart networking
   ```

5. IPアドレスが正しく設定されたか確認します。
   ```bash
   ip addr show
   ```
   
&nbsp;

# Gitのインストール
```bash
sudo apt update
sudo apt upgrade
sudo apt install git
```

&nbsp;

# Dockerのインストール
## 下記のページの手順通りにインストールする
  * https://docs.docker.com/engine/install/debian/
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

## インストールできたか確認する
```bash
sudo docker run hello-world
```

&nbsp;

# カメラを使用可能にする
## 下記のページの手順通りに設定する
  * https://zenn.dev/kobayutapon/articles/490d93ab683337
### 必要なライブラリをインストールする
```bash
sudo apt update
sudo apt install libcamera-apps libraspberrypi-bin libraspberrypi0
```

### raspi-configを設定する
`sudo raspi-config`のInterface Optionsの設定でLegacy Cameraをdisabledにする。

### デバイスツリーの設定をする
次に、/boot/config.txtにカメラ用のdevice treeの設定を追記します。<br>
Raspberry Pi Camera Module 3の場合は以下の通りになります。

```
dtoverlay=imx708
```

指定するパラメータは以下の通り（出展元はこちら：https://www.raspberrypi.com/documentation/computers/camera_software.html#introducing-the-raspberry-pi-cameras)

| Camera Module |	In /boot/firmware/config.txt |
| ---- | ---- |
| V1 camera (OV5647) |	dtoverlay=ov5647 |
| V2 camera (IMX219) |	dtoverlay=imx219 |
| HQ camera (IMX477) |	dtoverlay=imx477 |
| GS camera (IMX296) |	dtoverlay=imx296 |
| Camera Module 3 (IMX708) |	dtoverlay=imx708 |
| IMX290 and IMX327 |	dtoverlay=imx290,clock-frequency=74250000 or dtoverlay=imx290,clock-frequency=37125000 (both modules share the imx290 kernel driver; please refer to instructions from the module vendor for the correct frequency) |
| IMX378 |	dtoverlay=imx378 |
| OV9281 |	dtoverlay=ov9281 |

### カメラの接続確認方法
参考：https://geek.tacoskingdom.com/blog/68

カメラデバイスが認識されている場合、/dev/フォルダでvideo0が追加されているはずなので、以下のコマンドで確認します。
```bash
ls /dev/ | grep video
```

### その他のカメラ情報の確認コマンド
`v4l2-ctl --all`で認識されたカメラの情報を確認する。
`v4l2-ctl --list-formats-ext`でWidthとHeightのリストを確認する。

### 注意
`raspistill`は`libcamera`に置き換えられた。