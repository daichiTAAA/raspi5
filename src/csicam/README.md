# Raspberry Pi Camera Module V3からのビデオストリームをRTSP形式でビデオストリーム配信する方法
&nbsp;

# 共通セットアップ
## デバイスの初期設定を行う
* docs/0030_要素技術/0010_RaspberryPiのドキュメントを元に初期設定を行う

## 必要なパッケージをインストールする
```bash
sudo apt update
sudo apt upgrade
sudo apt install -y python3-pip python3-venv
```

## 無線LANのIPアドレスを固定する
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

# Raspberry Pi5用セットアップ方法
## 1. Raspberry Pi OS Lite(64bit)をセットアップし、RaspberryPi5にSSHで接続して実行する。

## 2. 下記のコマンドでaptパッケージとPythonパッケージをインストールする
Raspberry Pi 5の場合、
```bash
sudo apt-get update && sudo apt-get install -y \
    libcamera-ipa \
    libcamera0.2 \
    python3-libcamera \
    python3-picamera2 \
    ffmpeg
```

Raspberry Pi Zero 2 Wの場合、
```bash
sudo apt update
sudo apt install -y ffmpeg python3-opencv
```

venvで仮想環境を作成する。
```bash
cd ~/raspi5
python3 -m venv stream
source stream/bin/activate
```
既に作成済みの場合はアクティベートのみ行う。
```bash
cd ~/raspi5
source stream/bin/activate
```
pythonパッケージをインストールする
```bash
cd ~/raspi5/src/csicam
pip install --no-cache-dir -r requirements.txt
```

## 3. カメラで写真を撮影可能か確認する
```bash
cd ~/raspi5/src/csicam/csicam
python get_image.py
```

## 4. MediaMTXコンテナを実行する
```bash
cd ~/raspi5/src/csicam
sudo docker compose up
```

## 5. RaspberryPi5がRaspberry Pi Camera Module V3が撮影した動画を取得しMediaMTX経由でRTSP形式のビデオストリームを配信する
```bash
cd ~/raspi5/src/csicam/csicam
python serve_rtsp.py
```
    
## 6. 外部PCからのRTSPビデオストリームの受信
* VLC Media Playerをインストールする。
* 下記のURLをファイル→ネットワーク画面で、下記のURLを入力し表示する。
    ```
    rtsp://{RaspberryPi5 IP Address}:8554/stream
    ```

&nbsp;

# Raspberry Pi Zero 2 W用セットアップ方法
## 1. SSH接続
* Raspberry Pi OS Lite(32bit)をセットアップし、RaspberryPi Zero 2 WにSSHで接続して実行する。

## 2. 必要なパッケージのインストール
aptパッケージをインストールする
```bash
sudo apt-get update && sudo apt-get install -y ffmpeg libopencv-dev python3-opencv
```
venvで仮想環境を作成する。
```bash
cd ~/raspi5
python3 -m venv stream
source stream/bin/activate
```
既に作成済みの場合はアクティベートのみ行う。
```bash
cd ~/raspi5
source stream/bin/activate
```
pythonパッケージをインストールする
```bash
cd ~/raspi5/src/csicam
pip install --no-cache-dir -r requirements.txt
```

## 3. カメラで写真を撮影可能か確認する
```bash
cd ~/raspi5/src/csicam/csicam
python get_image.py
```

## 4. MediaMTXコンテナを実行する
```bash
cd ~/raspi5/src/csicam
sudo docker compose up
```

## 5. ビデオストリーム配信を実施する
Raspberry Pi Camera Module V3が撮影した動画を取得しMediaMTX経由でRTSP形式のビデオストリームを配信する。
```bash
cd ~/raspi5
source stream/bin/activate
cd ~/raspi5/src/csicam/csicam
python serve_rtsp.py
```
    
## 6. 外部PCからのRTSPビデオストリームの受信
* VLC Media Playerをインストールする。
* 下記のURLをファイル→ネットワーク画面で、下記のURLを入力し表示する。
```
rtsp://{RaspberryPi Zero 2 W IP Address}:8554/stream
```