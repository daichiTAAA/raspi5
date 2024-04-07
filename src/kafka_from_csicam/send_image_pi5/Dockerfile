FROM dtcooper/raspberrypi-os:python3.11-bookworm

RUN apt update -y && apt upgrade -y && apt install git vim -y

#libcamera
RUN apt install libcamera-tools libcamera-apps-lite -y
RUN apt install libcap-dev libcamera-dev -y
RUN apt install libatlas-base-dev libopenjp2-7 libkms++-dev libfmt-dev libdrm-dev -y
RUN pip install rpi-libcamera rpi-kms

#picamera2
RUN apt install -y python3-picamera2 --no-install-recommends
RUN pip install picamera2

WORKDIR /code

# 必要なPythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pythonスクリプトをコンテナにコピー
COPY produce_image.py .

# スクリプトを実行
CMD ["python", "produce_image.py"]