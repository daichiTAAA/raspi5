# 調査資料 - Raspberry Pi Zero 2 WでのWebRTC配信方法
<br>

# 作成記録
---
* 作成日時 2024/10/4 野田大一郎
* 更新日時
<br>

# 概要
---
* このドキュメントはRaspberry Pi Zero 2 WでのWebRTC配信方法の調査資料である。
<br>

# 対象読者
---
* このドキュメントはRaspberry Pi Zero 2 WでのWebRTC配信方法を確認したいエンジニア用である。
<br>

# 目的
---
* Raspberry Pi Zero 2 WでのWebRTC配信方法を記載する。
<br>


# 内容
---

# Raspberry Pi Camera v3を使用する場合

## レガシーカメラ設定を無効にする
```bash
sudo raspi-config
```
Interfacing Options → Legacy Camera → Noを選択し、再起動します。

## Raspberry Pi Cameraライブラリをインストールします
```bash
sudo apt update
sudo apt install libcamera-apps
```

## ffmpegをインストールします
```bash
sudo apt update
sudo apt install ffmpeg
```

## MediaMTXをインストールします
```bash
wget https://github.com/bluenviron/mediamtx/releases/download/v1.7.0/mediamtx_v1.7.0_linux_armv7.tar.gz
tar -xvzf mediamtx_v1.7.0_linux_armv7.tar.gz
```

## mediamtx.ymlファイルを編集します
```bash
nano mediamtx.yml
```
以下の内容をpaths:セクションに追加します。
```yaml
paths:
  cam:
    runOnInit: bash -c 'libcamera-vid -t 0 --camera 0 --nopreview --codec yuv420 --width 1280 --height 720 --inline --rotation 180 --framerate 15 -o - | ffmpeg -f rawvideo -pix_fmt yuv420p -s:v 1280x720 -r 15 -i /dev/stdin -c:v libx264 -preset ultrafast -tune zerolatency -f rtsp rtsp://localhost:$RTSP_PORT/$MTX_PATH'
    runOnInitRestart: yes
```

## WebRTCストリーム配信の開始
MediaMTXを起動します
```bash
./mediamtx
```

## WebRTCストリームの受信
WebRTCストリームにアクセスします。ブラウザで以下のURLを開きます。
```
http://<Raspberry PiのIPアドレス>:8889/cam
```