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
# 必要なライブラリのインストール
```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
ls /dev/video*
```

# CSIカメラが認識されているかの確認方法
```bash
v4l2-ctl --list-devices
```