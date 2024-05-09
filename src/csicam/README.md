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
    ffmpeg \
    libopencv-dev \
    python3-opencv
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

RaspberryPi 5の場合
```
rtsp://{RaspberryPi 5 Address}:8554/stream1
rtsp://{RaspberryPi 5 Address}:8554/stream2
```
RaspberryPi Zero 2 Wの場合
```
rtsp://{RaspberryPi Zero 2 W IP Address}:8554/stream
```

## 7. systemdを使用した自動実行設定
Bullseyeの起動時にPython仮想環境(venv)をアクティベートし、指定したPythonスクリプトを自動実行するには、以下の手順を実施するのがおすすめです。

1. まず、実行したいPythonスクリプトを作成し、パスを控えておきます(例: /home/pidn/raspi5/src/csicam/csicam/serve_rtsp.py)。

2. 次に、systemdを使ってサービスファイルを作成します。
sudo nano /etc/systemd/system/myscript.service
以下の内容を記述します。

[Unit]
Description=RTSP streaming
After=multi-user.target

[Service] 
User=pidn
WorkingDirectory=/home/pidn
ExecStart=/home/pidn/raspi5/stream/bin/python /home/pidn/raspi5/src/csicam/csicam/serve_rtsp.py

[Install]
WantedBy=multi-user.target

ExecStartの行で、venvのpythonのパスとスクリプトのパスを指定します。

3. サービスファイルを保存し、実行権限を付与します。
sudo chmod 644 /etc/systemd/system/myscript.service

4. systemdにサービスファイルを読み込ませ、自動起動を有効化します。
sudo systemctl daemon-reload
sudo systemctl enable myscript.service

5. 再起動して、スクリプトが自動実行されることを確認します。
sudo reboot

これで、Bullseyeの起動時にvenvがアクティベートされ、指定したPythonスクリプトが自動実行されるはずです。

スクリプトの内容によっては、ネットワークの準備ができる前に実行されて失敗する可能性もあるので、その場合はAfter=network.targetなどの指定が必要になります。