# 調査資料 - Miniforgeの使用方法の調査
&nbsp;
# 作成記録
---
* 作成日時 2024/5/5 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはMiniforgeの使用方法の調査結果の資料である。
&nbsp;
# 対象読者
---
* このドキュメントはMiniforgeの使用方法の調査結果を確認したいエンジニア用である。
&nbsp;
# 目的
---
* Miniforgeの使用方法の調査結果を記載する。
&nbsp;

# 内容
---
Linuxでminiforgeをインストールするには、以下の手順を実行します。

1. インストーラーのダウンロード
以下のコマンドを使って、適切なインストーラーをダウンロードします。
```bash
cd ~
wget -O Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
```
これにより、現在のアーキテクチャに適したインストーラーが`Miniforge3.sh`というファイル名でダウンロードされます。

2. インストーラーの実行
ダウンロードしたシェルスクリプトを、バッチモード(`-b`)オプションを付けて実行します。
```bash 
bash Miniforge3.sh -b -p "${HOME}/miniforge3"
```
`-p`オプションでインストール先のディレクトリを指定できます。上記の例では`${HOME}/miniforge3`を指定しています。

3. PATHの設定
インストールしたminiforgeのパスを.bashrcに追加します。
```bash
sudo nano ~/.bashrc
```
.bashrcに下記を追加します。
```
export PATH="${HOME}/miniforge3/bin:$PATH"
```

4. 初期化処理
`Run conda init`というエラーが出る場合は、下記のコードを実行してcondaを使用する前に、シェルの設定ファイルにcondaの初期化コードを追加する必要があります。これにより、conda activateなどのコマンドが正しく機能するようになります。
```bash
conda init bash
```

5. 動作確認
以下のコマンドでbase環境をアクティベートし、正しくインストールされたことを確認します。
```bash
conda activate
```

6. 仮想環境の削除方法
condaで仮想環境を削除するには、以下のコマンドを使用します。
```bash
conda remove -n [仮想環境名] --all
```