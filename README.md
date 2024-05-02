# raspi5

このリポジトリは、Raspberry Piを使用した3D復元プロジェクトのためのコードとドキュメントを含んでいます。

## 目次

- [要件定義](docs/0020_theme/0010_3DReconstruction/0010_requirements_definition/0010_requirements_definition.md)
- [基本設計](docs/0020_theme/0010_3DReconstruction/0020_basic_design_document/0010_目線カメラ画像からの3D復元.md)
- [要素技術](docs/0030_要素技術)
  - [Raspberry Pi](docs/0030_要素技術/0010_RaspberryPi)
  - [Docker](docs/0030_要素技術/0020_Docker)
  - [VSCode](docs/0030_要素技術/0030_VSCode)
  - [Poetry](docs/0030_要素技術/0040_Poetry)
  - [RTSP配信](docs/0030_要素技術/0060_RTSP配信)
  - [Cursor](docs/0030_要素技術/0080_Cursor)
  - [Rancher](docs/0030_要素技術/0100_Rancher)
- [ソースコード](src)
  - [CSIカメラ](src/csicam)
  - [Kafka](src/kafka) 
  - [AKHQ](src/akhq)
  - [Rancher](src/rancher)

## セットアップ

- [Raspberry Pi 5の初期設定](docs/0030_要素技術/0010_RaspberryPi/0010_RaspberryPi5初期設定方法.md)
- [Raspberry Pi Zero 2 Wの初期設定](docs/0030_要素技術/0010_RaspberryPi/0020_RaspberryPiZero2W初期設定方法.md)
- [DockerでのCSIカメラ使用方法](docs/0030_要素技術/0010_RaspberryPi/0030_DockerでのCSIカメラ使用方法.md)

## 使用方法

1. [Kafka](src/kafka)と[AKHQ](src/akhq)を起動
2. [Rancher](src/rancher)を起動し、クラスターを作成
3. [CSIカメラ](src/csicam)をRaspberry Pi Zero 2 Wで起動し、RTSPストリームを配信
4. Raspberry Pi 5上で3D復元処理を実行

## ライセンス

このプロジェクトはApache License 2.0ライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。