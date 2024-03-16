# 調査資料 - Gstreamerを使用したRTSPビデオストリーム配信
&nbsp;
# 作成記録
---
* 作成日時 2024/3/16 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはGstreamerを使用したRTSPビデオストリーム配信方法の調査資料である。
&nbsp;
# 対象読者
---
* このドキュメントはGstreamerを使用したRTSPビデオストリーム配信方法を確認したいエンジニア用である。
&nbsp;
# 目的
---
* Gstreamerを使用したRTSPビデオストリーム配信方法を記載する。
&nbsp;

# 内容
---
# RTSPサーバーの必要性
* FFmpegだけでは完全なRTSPサーバーの機能を提供することはできません。FFmpegはビデオのエンコードとストリーミングを行いますが、RTSPプロトコルの完全な実装は提供していません。

# Gstreamerを使用したRTSPサーバー
* 下記の記事のようにGitHubをクローンしビルドすれば使用可能とのこと。しかし、GitHubの更新が5年前で止まっているため採用を見送る。
https://dev.classmethod.jp/articles/amazon-kinesis-vidseo-streams-gstreamer-rtsp-server/