# 調査資料 - Raspberry Pi Picoの初期設定方法
&nbsp;
# 作成記録
---
* 作成日時 2024/5/5 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはRaspberry Pi Picoの初期設定方法の調査資料である。
&nbsp;
# 対象読者
---
* このドキュメントはRaspberry Pi Picoの初期設定方法を確認したいエンジニア用である。
&nbsp;
# 目的
---
* Raspberry Pi Picoの初期設定方法を記載する。
&nbsp;

# 内容
---
# 接続先Raspberry Pi 5の準備
* Raspberry Pi Picoを接続するRaspberry Pi 5を準備する。
* Raspberry Pi 5にSSH接続し、VSCodeに拡張機能であるMicroPicoをインストールする。
  * 参考：https://www.technicalife.net/vscode-micropython-devenv/
* コマンドパレットを開き Configure project を選択します。すると、 .vscode のフォルダが作成され、必要な設定ファイルなどの情報が出力されます。

<br>

# Raspberry Pi PicoへのMicroPythonファームウェアのインストール
Raspberry Pi 5のターミナルからRaspberry Pi PicoにMicroPythonファームウェアを書き込むには、以下の手順を実行します。

1. Raspberry Pi PicoをRaspberry Pi 5のUSBポートに接続します。その際、PicoのBOOTSELボタンを押しながら接続すると、マスストレージモードで起動します。

2. ターミナルを開き、MicroPythonファームウェアをダウンロードします。
   Raspberry Pi Picoの場合
   ```
   cd ~
   wget https://micropython.org/download/rp2-pico/rp2-pico-latest.uf2
   ```
   Raspberry Pi Pico Wの場合
   ```
   cd ~
   wget https://micropython.org/download/rp2-pico-w/rp2-pico-w-latest.uf2
   ```
   これにより、最新のMicroPythonファームウェアがカレントディレクトリにダウンロードされます。

3. lsblkコマンドでPicoがマウントされているデバイスを確認します。
   ```
   lsblk
   ```
   通常、/dev/sdaXのようなデバイス名で表示されます。

4. Picoがマウントされているディレクトリに移動します。
  Raspberry Pi PicoがマウントされているディレクトリはLinuxでは以下の方法で確認できます。
  Picoを接続する前と後でlsblkコマンドを実行し、新たに表示されたデバイス(例: sda1)がPicoに対応します。

  * dfコマンドでマウント状況を確認する。 

    ```bash
    df -h
    ```

    dfコマンドを実行すると、Picoのデバイス(例: /dev/sda1)がどのディレクトリにマウントされているか(例: /media/pi/RPI-RP2)が分かります。

  * /mediaディレクトリを確認する。

    デスクトップ版のUbuntuやRaspberry Pi OSでは、Picoは自動的に/mediaディレクトリ以下のどこかにマウントされます。

    ```bash
    ls /media/*/*
    ```

    以上の方法で、Raspberry Pi PicoがOSによって自動マウントされるディレクトリを特定できます。

  * Raspberry Pi Picoがマウントされていない場合
    
    自動でマウントするようにRaspberry Pi 5の/etc/fstabファイルに設定を追記します。
    ```bash
    sudo nano /etc/fstab
    ```
    fstabに以下の行を追加します。
    ```bash
    /dev/sda1 /media/pico vfat defaults,nofail,x-systemd.device-timeout=10 0 0
    ```
    Raspberry Pi 5を再起動します。この時、<br>
    Raspberry Pi 5にRaspberry Pi Picoを接続した状態でRaspberry Pi 5の電源を入れます。<br>
    この時、Raspberry Pi PicoのBOOTSELボタンを押した状態で電源を入れます。<br>
    Raspberry Pi 5の緑のランプがついて数秒経過したらBOOTSELボタンを離します。<br>
    この手順を実行する理由は、PicoのBOOTSELボタンを押しながら接続することで、マスストレージモードで起動し、<br>
    Raspberry Pi 5へのRaspberry Pi Picoのマウントトライのタイムアウト(fstabの設定に追記したdevice-timeoutの秒数でタイムアウトする)前に、<br>
    PicoのBOOTSELボタンを離すことでマウントするためです。

5. ダウンロードしたファームウェアをPicoにコピーします。
   Raspberry Pi Picoの場合
   ```
   cd /media/pico
   sudo cp ~/rp2-pico-latest.uf2 .
   ```
   Raspberry Pi Pico Wの場合
   ```
   cd /media/pico
   sudo cp ~/rp2-pico-w-latest.uf2 .
   ```
   ファームウェアのファイル名とパスは、手順2でダウンロードした場所に合わせて適宜変更してください。

6. ファームウェアの書き込みが完了すると、Picoは自動的に再起動し、通常モードで起動します。

以上の手順により、Raspberry Pi 5のターミナルからRaspberry Pi PicoにMicroPythonファームウェアを書き込むことができます。

<br>

# Raspberry Pi PicoをVS Code + MicroPicoで開発する環境構築手順

machineライブラリの補完やシリアル通信を利用したデバッグを可能にします。

## 1. micropy-cliのインストールとプロジェクト作成

Python3.10を使用した仮想環境にてmicorpy-cliをインストールする。<br>
Python3.12だとmicropyのcliコマンド実行時に依存関係エラーとなる。

```bash
pip install --upgrade micropy-cli
cd myproject
```

### 必要なスタブファイルのインストール
* スタブファイルとは、MicroPythonのライブラリやモジュールの型情報を含むファイルで、コード補完や型チェックに使用されます。micropy-cliはデフォルトでスタブファイルを必要とするため、プロジェクト作成前にスタブファイルをインストールする必要があります。
* 利用可能なスタブパッケージは以下のコマンドで検索できます。

```bash
micropy stubs search rp2
```
* 以下のコマンドを使ってスタブファイルをpipでインストールします

```bash
pip install -U micropython-rp2-pico_w-stubs
```

## 2. VS Codeの設定
* VSCodeのコマンドパレット(cmd+Shift+P)からMicroPico: Configure Projectを実行する
* `.vscode/settings.json`を開き、`python.languageServer`を`"Pylance"`に変更。

## 3. サンプルコードの実行

`flash.py`にサンプルコードを書き、Pymakrの「Run」ボタンでPicoに転送・実行。

```python
from machine import Pin
import time

led = Pin("LED", Pin.OUT)

while True:
    led.toggle()
    time.sleep(0.5)
```

以上の手順により、VS Code + MicroPico + micropy-cliを使ったRaspberry Pi Picoの開発環境が構築できます。この環境では、machineライブラリの補完、シリアル通信を使ったデバッグ、コードの転送・実行などが可能になり、IoT開発を効率的に進められます。

Picoの開発では、シリアルポートのパスを正しく指定することが重要です。OSごとの確認方法を覚えておくと良いでしょう。
