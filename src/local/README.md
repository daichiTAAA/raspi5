# ローカル用コード
* デスクトップアプリケーション
* モバイルアプリケーション

# Windows版のビルド時
ビルドしても`src/local/flutterapp/build/windows/x64/runner/runner.exe.manifest`ファイルが作成されずエラーとなる場合、<br>
下記のファイルを`src/local/flutterapp/build/windows/x64/runner/`フォルダに作成する。

`runner.exe.manifest`ファイル
```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <application xmlns="urn:schemas-microsoft-com:asm.v3">
    <windowsSettings>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
    </windowsSettings>
  </application>
</assembly>
```