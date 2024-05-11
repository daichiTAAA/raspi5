# Raspberry Pi 5からのビデオストリームを他のPCで受信し処理する
## 仮想環境の作成
### venvを使用する場合
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
cd ~/raspi5/src/stream_analysis
pip install --no-cache-dir -r requirements.txt
```

### condaを使用する場合
* docs/0030_要素技術/0130_Miniforgeを元にcondaをインストールしていることを前提とする。

condaで仮想環境を作成する。
```bash
conda create -n stream python=3.10
conda activate stream
cd ~/raspi5/src/stream_analysis
pip install -r requirements.txt
```

### ビデオストリームを受信し画像として保存する
```bash
cd ~/raspi5/src/stream_analysis/stream_analysis
python stream_to_image.py
```