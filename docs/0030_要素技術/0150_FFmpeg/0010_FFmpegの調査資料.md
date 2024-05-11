# 調査資料 - FFmpegの使用方法の調査
&nbsp;
# 作成記録
---
* 作成日時 2024/5/11 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはFFmpegの使用方法の調査結果の資料である。
&nbsp;
# 対象読者
---
* このドキュメントはFFmpegの使用方法の調査結果を確認したいエンジニア用である。
&nbsp;
# 目的
---
* FFmpegの使用方法の調査結果を記載する。
&nbsp;

# 内容
---
# LinuxでのLinuxコマンドを使用したFFmpegのインストール方法

Ubuntuでは、FFmpegはaptパッケージマネージャを使用して簡単にインストールできます。以下の手順に従ってください。

1. ターミナルを開き、以下のコマンドを実行してFFmpegをインストールします。

   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

2. インストールが完了したら、以下のコマンドでFFmpegのバージョンを確認します。

   ```bash
   ffmpeg -version
   ```

   FFmpegのバージョン情報が表示されれば、インストールは成功です。

3. FFmpegはデフォルトでシステムのPATHに追加されるため、別途パスを通す必要はありません。ターミナルからffmpegコマンドを直接実行できます。

   ```bash
   ffmpeg [オプション] [入力ファイル] [出力ファイル]
   ```

以上で、UbuntuでのFFmpegのインストールは完了です。FFmpegの詳細な使用方法については、公式ドキュメントやオンラインリソースを参照してください。

参考:
- [Ubuntu - ffmpeg package](https://launchpad.net/ubuntu/+source/ffmpeg)