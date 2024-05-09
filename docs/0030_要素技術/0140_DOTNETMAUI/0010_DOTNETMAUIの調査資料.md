# 調査資料 - .NET MAUIの使用方法の調査
&nbsp;
# 作成記録
---
* 作成日時 2024/5/9 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントは.NET MAUIの使用方法の調査結果の資料である。
&nbsp;
# 対象読者
---
* このドキュメントは.NET MAUIの使用方法の調査結果を確認したいエンジニア用である。
&nbsp;
# 目的
---
* .NET MAUIの使用方法の調査結果を記載する。
&nbsp;

# 内容
---
# VS Codeでdotnetコマンドを使用するためのセットアップ方法
VS CodeでdotnetコマンドラインツールとC#開発環境をセットアップするには、以下の手順を実施します。

1. .NET SDKをインストールする
- .NET公式サイトから、使用するOSに合わせて.NET SDKをダウンロードしてインストールします。
- これによりdotnetコマンドが使えるようになります。

2. VS Codeに拡張機能をインストールする
- VS Codeを起動し、サイドバーの拡張機能アイコンをクリックします。
- 検索ボックスに「C#」と入力し、C#拡張機能(OmniSharp)をインストールします。
- 他にも便利な拡張機能があるので、必要に応じてインストールしてください。

3. 新規プロジェクトを作成する
- ターミナルまたはコマンドプロンプトを開き、プロジェクトを作成するフォルダに移動します。
- 以下のコマンドを実行し、新規のC#コンソールアプリケーションプロジェクトを作成します。
  ```
  dotnet new console -o SampleApp
  code SampleApp
  ```
- 実行するとVS Codeが起動し、プロジェクトが開かれます。

4. ビルドと実行
- プロジェクトを開いた状態で、F5キーを押すとビルドと実行ができます。
- またはターミナルで以下のコマンドを実行します。
  ```
  dotnet run
  ```
- ビルドが成功すると、コンソールにHello Worldが出力されます。

5. デバッグとテスト
- VS Codeのデバッグ機能を使って、ブレークポイントを設定したりステップ実行ができます。
- dotnetコマンドでテストプロジェクトを作成し、テストを実行することもできます。
  ```
  dotnet new xunit -o SampleTest
  dotnet test
  ```

以上で、VS CodeとdotnetコマンドラインツールによるC#開発環境のセットアップは完了です。
コマンドラインベースで手軽にC#の開発ができるようになります。

<br>

# VS Codeでの.NET MAUIアプリケーションの作成方法
以下は、Visual Studio Codeを使用して.NET MAUIアプリケーションを作成する手順です。

1. Visual Studio Codeを開き、新しいターミナルを開きます。

2. 以下のコマンドを実行して、.NET MAUIアプリケーションのテンプレートをインストールします。

   ```
   dotnet new install Microsoft.Maui.Templates
   ```

3. 新しいディレクトリを作成し、そのディレクトリに移動します。

   ```
   cd src
   mkdir MauiVideoApp
   cd MauiVideoApp
   ```

4. 以下のコマンドを実行して、新しい.NET MAUIアプリケーションを作成します。

   ```
   dotnet new maui
   ```

   これにより、現在のディレクトリに.NET MAUIアプリケーションのプロジェクトが作成されます。

5. プロジェクトのターゲットフレームワークを更新する
    プロジェクトファイル（.csproj）を開きます。<br>
    TargetFramework要素を確認し、net8.0-maccatalystを追加します。
    ```
    <TargetFrameworks>net8.0-android;net8.0-ios;net8.0-maccatalyst</TargetFrameworks>
    ```
    ビルド時に警告が出る場合、警告が出ないようにするために<ItemGroup></ItemGroup>の中に下記を記載します。
    ```
    <PackageReference Include="Microsoft.Maui.Controls" Version="8.0.7" />
    ```
    ファイルを保存します。

6. 以下のコマンドを実行して、必要な依存関係をリストアします。
    Windowsの場合、<br>
    コマンドプロンプトまたはPowerShellを管理者として実行します。
    ```
    dotnet workload restore
    ```
    macの場合、
    ```
    sudo dotnet workload restore
    ```

7. Macをターゲットにしてビルドするための設定

    VS Codeで.NET MAUIプロジェクトをビルドする際に、適切なApple SDKが使用されるようにする。

    * XcodeをApp Storeからインストールするか、Apple Developer Websiteからダウンロードしてインストールします。
    * ターミナルで以下のコマンドを実行して、Xcodeのコマンドラインツールをインストールします。
      ```
      xcode-select --install
      ```
    * VS Codeの設定ファイルを開きます。
      * コマンドパレットで`Preference: Open User Settings(JSON)`を選択する
      * `settings.json` ファイルに以下の設定を追加します。
        ```json
        "omnisharp.sdkPath": "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"
        ```
        必要に応じて、XcodeのインストールパスとSDKのバージョンを適切なものに置き換えてください。
      * ファイルを保存します。
      これで、VS Codeが.NET MAUIプロジェクトをビルドする際に、指定されたApple SDKの場所を使用するようになります。
    * Properties/launchSettings.jsonを下記のように修正します。
      ```
      {
        "profiles": {
          "(Default)": {
            "commandName": "Project"
          },
          "Windows Machine": {
            "commandName": "MsixPackage",
            "nativeDebugging": false
          }
        }
      }
      ```
    * 注意点
      * Xcodeがデフォルトの場所にインストールされていない場合は、`omnisharp.sdkPath` の値を適切なパスに変更してください。
      * Apple SDKのバージョンは、インストールされているXcodeのバージョンによって異なる場合があります。必要に応じて、SDKのパスを調整してください。

8. プロジェクトを実行するには、以下のコマンドを実行します。

   ```
   cd src/MauiVideoApp
   dotnet build -f net8.0-maccatalyst
   dotnet run -f net8.0-maccatalyst
   ```

   アプリケーションがビルドされ、エミュレータまたは接続されたデバイスで実行されます。

9. アプリケーションのソースコードを編集するには、Visual Studio Code内のファイルを変更します。変更を加えた後、再度 `dotnet build` と `dotnet run` を実行して、アプリケーションを更新します。

以上が、Visual Studio Codeを使用して.NET MAUIアプリケーションを作成し、実行する基本的な手順です。プロジェクトの要件に応じて、追加の設定やカスタマイズが必要になる場合があります。

## 注意点

- .NET MAUIを使用するには、.NET 6以降のSDKがインストールされている必要があります。
- iOS や Android でアプリケーションを実行するには、それぞれの開発環境とSDKが適切に設定されている必要があります。
- アプリケーションのUI要素やロジックは、プロジェクト内の適切なファイルを編集することで実装できます。

Visual Studio Codeは、.NET MAUIアプリケーションの開発に適した軽量で拡張性の高いIDEです。必要に応じて、拡張機能をインストールしてさらに機能を拡張することができます。

<br>

# .NET MAUIとBlazorを使用したRTSPストリームの表示

.NET MAUIとBlazorを組み合わせて、RTSPビデオストリームをアプリケーションのウィンドウ内に表示することができます。以下は、その方法の概要です。

1. .NET MAUIアプリケーションプロジェクトにBlazorのサポートを追加します。
MauiProgram.cs`ファイルを開き、`CreateMauiVideoApp`メソッド内に以下のコードを追加します。
   ```csharp
   builder.Services.AddMauiBlazorWebView();
   ```

2. `LibVLCSharp.Blazor` ライブラリをNuGetパッケージマネージャからインストールします。このライブラリは、BlazorアプリケーションでLibVLCを使用するために必要です。

   ```
   Idotnet add package LibVLCSharp.Blazor
   ```

3. `Pages`ディレクトリを作成し、その中に`VideoView.razor`ファイルを作成します。以下のコードを`VideoView.razor`に追加します。

   ```razor
   @page "/videoview"
   @using LibVLCSharp.Blazor
   @inject LibVLC LibVLC

   <h3>Video Player</h3>

   <VideoView MediaPlayer="@MediaPlayer" />

   @code {
       private MediaPlayer MediaPlayer;

       protected override void OnInitialized()
       {
           base.OnInitialized();

           MediaPlayer = new MediaPlayer(LibVLC);
           var media = new Media(LibVLC, "rtsp://your-camera-url");
           MediaPlayer.Media = media;
           MediaPlayer.Play();
       }
   }
   ```
   必要に応じて、`rtsp://your-camera-url`をネットワークカメラのRTSPストリームのURLに置き換えてください。

4. `MainPage.xaml`ファイルを開き、以下のコードを追加して、Blazorコンポーネントを呼び出します。

  ```xml
  <BlazorWebView HostPage="wwwroot/index.html">
  <Router AppAssembly="{}{typeof(Main).Assembly}">
  <Found Context="routeData">
  <RouteView RouteData="@routeData" DefaultLayout="{}{typeof(MainLayout)}" />
  <FocusOnNavigate RouteData="@routeData" Selector="h1" />
  </Found>
  <NotFound>
  <LayoutView Layout="{}{typeof(MainLayout)}">
  <p role="alert">Sorry, there's nothing at this address.</p>
  </LayoutView>
  </NotFound>
  </Router>
  </BlazorWebView>
  ```

   必要なネームスペースを追加することを忘れないでください。

5. 以下のコマンドを実行して、必要な依存関係をリストアします。
  ```bash
  dotnet restore
  ```

6. プロジェクトを実行するには、以下のコマンドを実行します。
   ```
   cd src/MauiVideoApp
   dotnet build -f net8.0-maccatalyst
   dotnet run -f net8.0-maccatalyst
   ```

これにより、.NET MAUIアプリケーションとBlazorを組み合わせて、RTSPビデオストリームをアプリケーションのウィンドウ内に表示することができます。Blazorコンポーネントは、指定されたRTSPストリームを再生し、.NET MAUIアプリケーションのレイアウト内に埋め込まれます。

## 注意点
- .NET MAUIとBlazorを使用するには、.NET 6以降のSDKがインストールされている必要があります。
- iOSやAndroidでアプリケーションを実行するには、それぞれの開発環境とSDKが適切に設定されている必要があります。
- アプリケーションのUI要素やロジックは、プロジェクト内の適切なファイルを編集することで実装できます。
- Blazorコンポーネントは、`Pages`ディレクトリ内に`.razor`ファイルとして作成します。
- `LibVLCSharp.Blazor`は、ネットワークカメラのRTSPストリームを再生するために使用されるライブラリの一例です。他のライブラリやカスタムコードを使用することもできます。

以上が、.NET MAUIとBlazorを使用してRTSPビデオストリームをアプリケーションのウィンドウ内に表示する方法の概要です。
