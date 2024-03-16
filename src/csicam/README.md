# Raspberry Pi Camera Module V3からのビデオストリームをRTSP形式でビデオストリーム配信する方法
## セットアップ方法
1. Raspberry Pi OS Lite(64bit)をセットアップし、RaspberryPi5にSSHで接続して実行する。
2. 下記のコマンドでaptパッケージとPythonパッケージをインストールする
    ```bash
    sudo apt-get update && sudo apt-get install -y \
        libcamera-ipa \
        libcamera0.2 \
        python3-libcamera \
        python3-picamera2 \
        ffmpeg
    ```
    ```bash
    cd src/csicam
    poetry install
    poetry shell
    ```
3. MediaMTXコンテナのDocker Comoposeを修正する
   下記のMTX_WEBRTCADDITIONALHOSTSにRaspberryPi5のIPアドレスを記載する
    ```bash
    version: '3'
    services:
    mediamtx:
        # image: bluenviron/mediamtx:latest-ffmpeg-rpi
        image: bluenviron/mediamtx:latest
        environment:
        - MTX_PROTOCOLS=tcp
        - MTX_WEBRTCADDITIONALHOSTS=192.168.0.3
        ports:
        - "8554:8554"
        - "1935:1935"
        - "8888:8888"
        - "8889:8889"
        - "8890:8890/udp"
        - "8189:8189/udp"
        restart: unless-stopped
    ```
4. MediaMTXコンテナを実行する
    ```bash
    cd src/csicam
    docker compose up
    ```
5. RaspberryPi5がRaspberry Pi Camera Module V3が撮影した動画を取得しMediaMTX経由でRTSP形式のビデオストリームを配信する
    ```bash
    cd src/csicam/csicam
    python serve_rtsp.py
    ```
6. 外部PCからのRTSPビデオストリームの受信
* VLC Media Playerをインストールする。
* 下記のURLをファイル→ネットワーク画面で、下記のURLを入力し表示する。
    ```
    rtsp://{RaspberryPi5 IP Address}:8554/stream
    ```