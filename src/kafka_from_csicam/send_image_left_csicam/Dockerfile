FROM python:3.11

# 必要なパッケージのインストール
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    gcc \
    libcap-dev
    # libcamera-ipa \
    # libcamera0.2 \
    # python3-libcamera \
    # python3-picamera2
# 作業ディレクトリの作成
WORKDIR /app

# 必要なPythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pythonスクリプトをコンテナにコピー
COPY produce_image.py .

# スクリプトを実行
CMD ["python", "produce_image.py"]