# チュートリアル - Poetry
&nbsp;
# 作成記録
---
* 作成日時 2024/3/15 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはPoetryのチュートリアルである。
&nbsp;
# 対象読者
---
* このドキュメントはPoetryの使用方法を確認したいエンジニア用である。
&nbsp;
# 目的
---
* Poetryの使用方法を記載する。
&nbsp;

# 内容
---
# 概要
Poetryは、Pythonプロジェクトの依存関係管理とパッケージ管理を簡素化するためのツールです。
Poetryを使用すれば、Condaを使用しなくても仮想環境を作成および管理できます。Poetryは、プロジェクトごとに独立した仮想環境を作成し、依存関係を管理するために使用されます。

- Poetryは、Pythonプロジェクトの依存関係を宣言的に管理するためのツールです。
- プロジェクトの依存関係は、`pyproject.toml`ファイルに記述されます。
- Poetryは、依存関係の解決、仮想環境の作成、パッケージのインストールなどを自動的に行います。
- プロジェクトのビルド、パッケージ化、公開などのタスクも簡単に実行できます。

# メリット
1. 依存関係の宣言的な管理:
   - `pyproject.toml`ファイルを使用して、プロジェクトの依存関係を明確に宣言できます。
   - 依存関係のバージョンを指定することで、再現性のあるビルドが可能になります。

2. 仮想環境の自動作成:
   - `poetry install`コマンドを実行すると、Poetryが自動的に仮想環境を作成します。
   - プロジェクトごとに独立した仮想環境を持つことができ、依存関係の衝突を回避できます。

3. 依存関係の解決:
   - Poetryは、依存関係の競合を自動的に解決します。
   - 依存関係のバージョン制約を満たすように、適切なバージョンの依存関係がインストールされます。

4. ビルドと公開の簡素化:
   - `poetry build`コマンドを使用して、プロジェクトのビルドとパッケージ化を簡単に行えます。
   - `poetry publish`コマンドを使用して、パッケージをPyPIなどのリポジトリに公開できます。

5. ロックファイルによる再現性の確保:
   - Poetryは、`poetry.lock`ファイルを生成し、プロジェクトの依存関係の正確なバージョンを記録します。
   - ロックファイルを使用することで、異なる環境でも同じ依存関係を確実にインストールできます。

6. 統合されたパッケージ管理:
   - Poetryは、パッケージの追加、削除、更新などの操作を簡単に行えます。
   - `poetry add`、`poetry remove`、`poetry update`などのコマンドを使用して、依存関係を管理できます。

Poetryは、Pythonプロジェクトの管理を簡素化し、依存関係の問題を解決するための強力なツールです。仮想環境の自動作成、依存関係の解決、ビルドと公開の簡素化など、開発者にとって多くのメリットがあります。Poetryを使用することで、プロジェクトの設定や管理に関する手間を減らし、開発に集中することができます。

# 使用方法
Poetryは、Pythonでコマンドラインから詩を生成するためのツールです。以下にPoetryの基本的な使用方法を説明します。
## インストール方法
1. インストール:
   - Poetryの公式サイト（https://python-poetry.org/docs/#installation）に記載された手順に従って、Poetryをインストールします。
     - pipxをインストールします。
      
        On macOS:
        ```bash
        brew install pipx
        pipx ensurepath
        ```
        On Linux:
        Ubuntu 23.04 or above
        ```bash
        sudo apt update
        sudo apt install pipx
        pipx ensurepath
        ```
        Ubuntu 22.04 or below
        ```bash
        python3 -m pip install --user pipx
        python3 -m pipx ensurepath
        ```
        On Windows:
        Install via Scoop:
        ```bash
        scoop install pipx
        pipx ensurepath
        ```
        Install via pip (requires pip 19.0 or later)
        ```bash
        # If you installed python using Microsoft Store, replace `py` with `python3` in the next line.
        py -m pip install --user pipx
        ```
      - poetryをインストールします。
        ```bash
        pipx install poetry
        ```
      - poetryのパスが通っていない場合は~/.bashrcに`PATH="$PATH":Poetryのbinフォルダのパス`を記載してパスを通します。

## poetry newを使用する場合
2. 新しいプロジェクトの作成:
   - 新しいディレクトリを作成し、そのディレクトリ内で以下のコマンドを実行します。
     ```
     poetry new my-project
     ```
   - これにより、`my-project`という名前の新しいプロジェクトが作成されます。
   - 作成したプロジェクトのディレクトリに移動します。

3. 依存関係の追加:
   - プロジェクトで必要なパッケージを追加するには、以下のコマンドを使用します。
     ```
     poetry add package-name
     ```
   - 開発時のみ必要な依存関係を追加する場合は、`--dev`オプションを使用します。
     ```
     poetry add --dev package-name
     ```

4. 仮想環境の作成と有効化:
   - 以下のコマンドを実行して、プロジェクト用の仮想環境を作成します。
     ```
     poetry install
     ```
   - 仮想環境を有効化するには、以下のコマンドを使用します。
     ```
     poetry shell
     ```

5. スクリプトの実行:
   - Poetryで管理されているプロジェクト内でPythonスクリプトを実行するには、以下のコマンドを使用します。
     ```
     poetry run python script.py
     ```

6. パッケージのビルドと公開:
   - プロジェクトをパッケージ化してディストリビューションファイルを作成するには、以下のコマンドを使用します。
     ```
     poetry build
     ```
   - パッケージを公開するには、以下のコマンドを使用します。
     ```
     poetry publish
     ```

7. その他の便利なコマンド:
   - `poetry update`: 依存関係を最新のバージョンに更新します。
   - `poetry remove package-name`: 依存関係からパッケージを削除します。
   - `poetry show`: インストールされているパッケージの一覧を表示します。

## poetry initを使用する場合
2. プロジェクトのディレクトリに移動します。
   ```
   cd my-project
   ```

3. `pyproject.toml`ファイルを作成するために、以下のコマンドを実行します。
   ```
   poetry init
   ```

4. 対話式のプロンプトに従って、プロジェクトの詳細を入力します。

5. 必要な依存関係を追加します。
   ```
   poetry add package-name
   ```

6. 仮想環境を作成し、依存関係をインストールします。
   ```
   poetry install
   ```

これで、プロジェクト用の仮想環境が作成され、指定された依存関係がインストールされます。仮想環境を有効化するには、`poetry shell`コマンドを使用します。

Poetryには他にも多くの機能がありますが、これらは基本的な使用法の一部です。詳細については、Poetryの公式ドキュメント（https://python-poetry.org/docs/）を参照してください。

# poetry initとpoetry newの使い分け
`poetry init`と`poetry new`は、どちらもPoetryを使用して新しいプロジェクトを開始するためのコマンドですが、それぞれ異なる目的と動作を持っています。

1. `poetry init`:
   - 既存のプロジェクトディレクトリ内で使用されます。
   - 対話式のプロンプトに従って、プロジェクトの詳細（名前、バージョン、説明など）を入力できます。
   - `pyproject.toml`ファイルを生成しますが、プロジェクトの構造は作成しません。
   - 既存のコードベースに対してPoetryを導入する場合や、カスタムプロジェクト構造を持つ場合に適しています。

2. `poetry new`:
   - 新しいプロジェクトを始めるために使用されます。
   - プロジェクト名を引数として受け取ります。
   - プロジェクトのディレクトリ構造を自動的に作成します。
   - 以下のようなファイルとディレクトリが作成されます：
     - `pyproject.toml`: プロジェクトの設定ファイル
     - `README.md`: プロジェクトの説明ファイル
     - `src/`: プロジェクトのソースコードディレクトリ
     - `tests/`: テストコードディレクトリ
   - プロジェクトの基本的な構造を自動的に生成するため、新しいプロジェクトを素早く開始できます。

つまり、`poetry init`は既存のプロジェクトにPoetryを導入する場合や、カスタムプロジェクト構造を持つ場合に使用し、`poetry new`は新しいプロジェクトを始める際に使用して、プロジェクトの基本的な構造を自動的に生成するためのコマンドです。

新しいプロジェクトを始める場合は`poetry new`を使用し、既存のプロジェクトにPoetryを導入する場合や、カスタムプロジェクト構造が必要な場合は`poetry init`を使用するのが一般的な使い分けです。

# VS CodeでのPoetryの使用方法
1. **前提条件の確認**
   - VS Codeがインストールされていること。
   - Python Extension for Visual Studio Codeがインストールされていること。
   - Poetryがインストールされていること。

2. **Poetryのパスを確認する**
   - ターミナルやコマンドプロンプトで`poetry --version`を実行し、Poetryがインストールされていることを確認します。
   - 同じくターミナルで`which poetry`（macOS/Linux）または`Get-Command poetry`（Windows PowerShell）、`where poetry`（Windows CMD）を実行し、Poetryのフルパスを確認します。

3. **VS Codeの設定を更新する**
   - VS Codeの`settings.json`を開き（コマンドパレットから`Preferences: Open Settings (JSON)`を選択）、`"python.poetryPath"`にPoetryのフルパスを設定します。
      ```json
      {
         "python.poetryPath": "path/to/poetry"
      }
      ```

4. **Poetryの仮想環境をVS Codeで使用する**
   - VS CodeでPythonのインタープリタを選択する際、Poetryで作成された仮想環境を選ぶことができます。右下のインタープリタ選択部分から、Poetryが管理する仮想環境を選択します。
   - 仮想環境が自動で検出されない場合は、`Ctrl+Shift+P`（または`Cmd+Shift+P` on macOS）を押してコマンドパレットを開き、「Python: Select Interpreter」を検索し、実行してから、リストから手動で環境を選択します。
   - または、`poetry install`や`poetry shell`でPoetryの仮想環境を有効にした状態で`which python`でpythonのパスを確認し、右下のインタープリタ選択部分のパスを追加ボタンで開いた入力欄にpythonのパスを入力します。

5. **Poetryを使用して依存関係を管理する**
   - VS Codeの統合ターミナルを開き（`View > Terminal`）、Poetryコマンドを使用してプロジェクトの依存関係を追加、更新、またはインストールします。例えば、`poetry add requests`で新しいライブラリを追加できます。
   - `poetry install`を実行して、`pyproject.toml`に記載された依存関係をインストールし、プロジェクトの仮想環境をセットアップします。

6. **プロジェクトの開発を開始する**
   - Poetryの仮想環境がアクティブになっていることを確認し、プロジェクトの開発を開始します。VS CodeのPython Extensionは、選択されたインタープリタに基づいてLintingやIntelliSense、デバッグ機能を提供します。

これらのステップに従って、VS CodeでPoetryを使用してPythonプロジェクトの開発を行うことができます。Poetryは、依存関係の管理を簡単にし、プロジェクトが異なる環境間で一貫して動作するようにします。