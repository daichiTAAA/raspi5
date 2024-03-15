# 調査資料 - CSIカメラの使用方法
&nbsp;
# 作成記録
---
* 作成日時 2024/3/15 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはCSIカメラの使用方法の調査資料である。
&nbsp;
# 対象読者
---
* このドキュメントはCSIカメラの使用方法を確認したいエンジニア用である。
&nbsp;
# 目的
---
* CSIカメラの使用方法を記載する。
&nbsp;

# 内容
---
# CSIカメラが認識されているかの確認方法
```bash
rpicam-hello
```

# 必要なライブラリのインストール
* 下記の記事を参考にする。<br>
  * https://sozorablog.com/camera-module-v3/
  * https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf?_gl=1*1xozib*_ga*MTMyODA4NjAzMy4xNzAxMDk0MjMz*_ga_22FD70LWDS*MTcxMDUxMzcwNy42LjEuMTcxMDUxMzgyOC4wLjAuMA..
  ```bash
  sudo apt update
  sudo apt install -y python3-picamera2
  ```

# Python中でのインポート
* 下記の通りaptでインストールしたpicamera2パッケージのパスをPythonスクリプトに追加する。
  * この時、RaspberryPi OS Liteの場合GUI表示機能を持たないためプレビューをNULLに設定する必要がある。
    ```python
    import sys

    sys.path.append("/usr/lib/python3/dist-packages")
    print(sys.path)

    from picamera2 import Picamera2, Preview

    picam2 = Picamera2()
    # 画像をプレビューしない設定をする
    picam2.start_preview(Preview.NULL)

    # カメラ画像を保存する
    picam2.start_and_capture_file("test.jpg")
    ```
* インテリセンスを使用するためにpoetryでpicamera2をインストールする
  ```bash
  poetry add picamera2
  ```