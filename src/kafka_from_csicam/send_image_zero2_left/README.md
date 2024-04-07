# send_image_zero2_left

このディレクトリには、RaspberryPi Zero 2 WからKafkaトピックに画像を送信するためのPythonスクリプトが含まれています。

## 必要条件

- RaspberryPi Zero 2 W
- カメラモジュール
- Kafkaブローカーへのネットワーク接続

## セットアップ
### 必要なパッケージのインストール
aptパッケージをインストールする
```bash
sudo apt update
sudo apt upgrade
sudo apt install -y python3-pip python3-venv
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
cd ~/raspi5/src/kafka_from_csicam/send_image_zero2_left
pip install --no-cache-dir -r requirements.txt
```

### CMSメモリを増やす
/boot/config.txtファイルを編集し、以下の行を追加または修正してCMSメモリを増やす。
```bash
sudo nano /boot/config.txt
```
下記を追加する。
```
dtoverlay=vc4-kms-v3d,cma-320
```

## 使用方法

### 1. スクリプトを実行します:

```bash
cd ~/raspi5/src/kafka_from_csicam/send_image_zero2_left
python produce_image.py
```

### 2. スクリプトは、一定間隔でカメラから画像をキャプチャし、Kafkaトピックにpublishします。

### 3. Ctrl+Cを押すと、スクリプトが停止します。

## トラブルシューティング

- Kafkaブローカーへの接続に問題がある場合は、ネットワーク設定とファイアウォールルールを確認してください。
- カメラモジュールが正しく接続されていることを確認してください。