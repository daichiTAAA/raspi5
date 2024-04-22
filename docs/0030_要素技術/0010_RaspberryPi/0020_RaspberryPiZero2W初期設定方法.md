# 調査資料 - RaspberryPi Zero 2 Wの初期設定方法
&nbsp;
# 作成記録
---
* 作成日時 2024/4/3 野田大一郎
* 更新日時 2024/4/22 野田大一郎
&nbsp;
# 概要
---
* このドキュメントはRaspberryPi Zero 2 Wの初期設定方法の調査資料である。
&nbsp;
# 対象読者
---
* このドキュメントはRaspberryPi Zero 2 Wの初期設定方法を確認したいエンジニア用である。
&nbsp;
# 目的
---
* RaspberryPi Zero 2 Wの初期設定方法を記載する。
&nbsp;

# 内容
---
# 初期設定方法
* RaspberryPi5の初期設定方法とほぼ同じ
* メモリが少ないため64bitでなく、RaspberryPiOS Lite 32bitの方が良い。しかし、confluent-kafkaは64bitでないと使用できない。そのため、もしKafkaを使用する場合は64bit版を使用する。
* 無線LANは2.4GHzのみ使用可能なためSSIDは5GHz用でなく、2.4GHz用を使用することに注意する

&nbsp;

# 無線LAN接続がうまくいかない場合の対処方法
* 有線LANで接続し、下記の方法でSSIDとパスワードを再度設定する。この時2.4GHzのSSIDを使用すること。
  * https://qiita.com/nanbuwks/items/9a1d46c22e898178015c<br>
    下記のコマンドを実行しwpa_supplicant.confファイルを開き、
    ```bash
    sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
    ```
    下記の内容を記載する。この時、SSIDは2.4GHzのものを使用し、パスワードも再度入力し直す。この時、""で囲むことを忘れないようにする。
    ```
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=JP
    network={
    ssid="myssid"
    psk="mypassphrase"
    }
    ```

&nbsp;

# 無線LANも有線LANも接続しており、IPアドレスを直接使用すればSSH接続できるが、ドメイン名を使用してSSH接続できない場合の対処方法
## IPアドレスを固定し固定IPアドレスでSSH接続する
* 使用しているIPアドレスの調査コマンド<br>
  `nmap -sn 192.168.0.0/24`
* SSH接続コマンド<br>
  `ssh {username}@{IPAddress}`
### IPアドレスを確認しIPアドレスを直接使用しSSH接続する
### IPアドレスを固定する
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

例：無線LANのIPアドレスを固定する
```
auto wlan0
iface wlan0 inet static
    address 192.168.0.201
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

ただし、IPアドレスを固定する際は、ネットワーク管理者と調整し、IPアドレスの重複を避けるようにしてください。

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