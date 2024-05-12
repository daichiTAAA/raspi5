# 調査資料 - Flutterの使用方法の調査
&nbsp;
# 作成記録
---
* 作成日時 2024/5/11 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはFlutterの使用方法の調査結果の資料である。
&nbsp;
# 対象読者
---
* このドキュメントはFlutterの使用方法の調査結果を確認したいエンジニア用である。
&nbsp;
# 目的
---
* Flutterの使用方法の調査結果を記載する。
&nbsp;

# 内容
---
# インストール方法
1. Flutterの公式ページから取得<br>
https://docs.flutter.dev/get-started/install

# プロジェクトの作成方法
1. Flutterの公式ページドキュメントを参照する<br>
https://docs.flutter.dev/get-started/test-drive

# Flutterのデバック方法
1. VSCodeの左側のRun and Debugアイコンを選択する。
2. 上側に表示されるRUN AND DEBUGでFlutterを選択する。

# Cocoapodsのインストール方法
参考：渡部 陽太. Flutter実践開発 ── iPhone／Android両対応アプリ開発のテクニック WEB+DB PRESS plus (p.42). Kindle 版. 
macOS標準のRubyのバージョンではCocoaPodsがインストールできない場合があります。そのようなときの対処法の一例を紹介します。Rubyのバージョン管理ツールであるrbenvを使ってRubyのバージョンを上げます。まず、rbenvをインストールするためのパッケージマネージャであるHomebrewを用いてインストールします。Homebrewのインストールに関する詳細は公式Webサイト（https://docs.brew.sh/Installation）に記載があります。

```bash
# Homebrewをインストール
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Homebrewにパスを通す
echo "export PATH=\"\$PATH:/opt/homebrew/bin\"" >> ~/.zshenv
#実行中のシェルにパスを適用
. ~/.zshenv
```
続いて、rbenvをインストールします。
```bash
# rbenvをインストール
brew install rbenv ruby-build
# rbenvにパスを通す
echo "eval \"\$(rbenv init - zsh)\"" >> ~/.zshrc
# 実行中のシェルにパスを適用
. ~/.zshrc
```
rbenvを使ってRubyをインストールします。今回は3.2.1をインストールします。
```bash
# バージョン3.2.1のRubyをインストール
rbenv install 3.2.1
# グローバルのRubyのバージョンを3.2.1に設定
rbenv global 3.2.1
```
以下のコマンドでRubyのバージョンを確認しましょう。
```bash
# Rubyのバージョンを出力
ruby --version
```

バージョン2.7.5が適用されていない場合はターミナルを再起動してください。続いて、CocoaPodsをインストールします。
```bash
# CocoaPodsをインストール
gem install cocoapods
```

以下のコマンドでCocoaPodsのバージョンを確認しましょう。
```bash
# CocoaPodsのバージョンを出力
pod --version
```
無事にバージョンが表示されれば完了です。

# MacOSでのデバック方法
macOSでネットワークにアクセスするには、特定のエンタイトルメントを要求する必要があります。そのためには、Flutterのプロジェクトフォルダ下の、macos/Runner/DebugProfile.entitlementsを開き、以下のキーと値のペアを追加します。

<key>com.apple.security.network.client</key>
<true/>

次に、macos/Runner/Release.entitlementsでも同じことを行います。

変更を反映するには、アプリを停止して再起動する必要があります。

詳細については、ドキュメントの[エンタイトルメントの設定](https://docs.flutter.dev/platform-integration/macos/building#setting-up-entitlements)を参照してください。