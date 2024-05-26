# 基本設計書:  WebSocketを使用した動画送付
<br>

# 作成記録
---
* 作成日時 2024/5/26 野田大一郎
* 更新日時
<br>

# 概要
---
* このドキュメントはWebSocketを使用した動画送付の基本設計書である。
<br>

# 対象読者
---
* このドキュメントはWebSocketを使用した動画送付の基本設計書を確認したいエンジニア用である。
<br>

# 目的
---
* WebSocketを使用した動画送付の基本設計を記載する。
<br>

# 内容
---
## 背景

動画ストリーミングは、エンターテインメント、教育、ビジネスなど多くの分野で重要な役割を果たしています。特に、リアルタイムでの動画配信は、会議、ライブイベント、監視システムなどで広く利用されています。これらの用途では、セキュアな通信と高い可用性が求められます。

## 課題

1. **セキュアな通信**: 動画データの盗聴や改ざんを防ぐために、通信を暗号化する必要があります。
2. **リアルタイム性**: 動画ストリーミングはリアルタイムで行われるため、低遅延でのデータ伝送が求められます。
3. **スケーラビリティ**: 動画ストリーミングの需要に応じて、システムが自動的にスケールアップ/スケールダウンする必要があります。
4. **認証と認可**: 不正アクセスを防ぐために、適切な認証と認可の仕組みが必要です。

## 解決策

Azure Container Appsを使用して、FastAPI製のアプリケーションをホストし、WebSocketを使用して自宅PCから動画ストリームをセキュアに送信します。以下の手順で実装します。

### 1. HTTPSを使用したセキュアな通信

Azure Container Appsでは、デフォルトでHTTPSが有効になっています。カスタムドメインを使用する場合は、SSL証明書を設定する必要があります。

### 2. FastAPIアプリケーションの設定

FastAPIアプリケーションを設定し、動画ストリームを受信するエンドポイントを作成します。

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            await websocket.send_bytes(data)
    except WebSocketDisconnect:
        print("Client disconnected")

@app.get("/")
async def get():
    return {"message": "WebSocket endpoint is /ws"}
```

### 3. 自宅PCから動画を送信

Pythonの`websockets`ライブラリを使用して、WebSocketを通じて動画データを送信します。

```python
import asyncio
import websockets
import cv2

async def send_video():
    uri = "wss://your-container-app-domain/ws"
    async with websockets.connect(uri) as websocket:
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            await websocket.send(buffer.tobytes())
            await asyncio.sleep(0.01)

asyncio.get_event_loop().run_until_complete(send_video())
```

### 4. セキュリティ対策

#### 認証と認可

JWT（JSON Web Token）を使用して、認証を行います。

```python
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

class TokenData(BaseModel):
    username: str | None = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            await websocket.send_bytes(data)
    except WebSocketDisconnect:
        print("Client disconnected")

@app.get("/")
async def get():
    return {"message": "WebSocket endpoint is /ws"}
```

## 選定技術

- **Azure Container Apps**: サーバーレスのコンテナプラットフォームで、自動スケーリングやイベント駆動型の処理が可能。
- **FastAPI**: 高速なWebフレームワークで、WebSocketのサポートも充実。
- **WebSocket**: リアルタイム通信を実現するためのプロトコル。
- **JWT**: 認証と認可のためのトークンベースの仕組み。

## セキュリティ

- **HTTPS**: 通信の暗号化を行い、データの盗聴や改ざんを防止。
- **JWT**: 認証と認可を行い、不正アクセスを防止。

## 技術選定理由

- **Azure Container Apps**: サーバーレスで自動スケーリングが可能なため、コスト効率が良く、WebSocketのサポートもあるため、動画ストリーミングに適しています。
- **FastAPI**: 高速でシンプルなWebフレームワークであり、WebSocketのサポートも充実しているため。

## 構想

Azure Container Appsを使用して、FastAPI製のアプリケーションをホストし、自宅PCからの動画ストリームをセキュアに受信し、外部からの指示に従って動画を配信するシステムを構築します。

## 具体的な構想

1. **Azure Container Appsの設定**:
   - AzureポータルでAzure Container Appsを作成し、HTTPSを有効にします。
   - カスタムドメインとSSL証明書を設定します。

2. **FastAPIアプリケーションのデプロイ**:
   - FastAPIアプリケーションをDockerコンテナとしてビルドし、Azure Container Registryにプッシュします。
   - Azure Container Appsにデプロイし、WebSocketエンドポイントを公開します。

3. **自宅PCからの動画送信**:
   - Pythonの`websockets`ライブラリを使用して、カメラから取得した動画データをWebSocketを通じて送信します。

4. **セキュリティ対策**:
   - JWTを使用して認証と認可を行い、セキュアな通信を実現します。

これにより、Azure Container Appsを使用して、セキュアでスケーラブルな動画ストリーミングシステムを構築できます。

Citations:
[1] http://blog.pamelafox.org/2023/03/deploying-containerized-fastapi-app-to.html
[2] https://learn.microsoft.com/en-us/azure/developer/python/tutorial-containerize-simple-web-app
[3] https://link.springer.com/article/10.1007/s11042-024-18763-2
[4] https://www.dacast.com/blog/secure-online-video-platform/
[5] https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/azure-container-apps-security-baseline
[6] https://learn.microsoft.com/en-us/azure/architecture/ai-ml/idea/video-ingestion-object-detection-edge-cloud
[7] https://azure.microsoft.com/en-us/products/container-apps
[8] https://antmedia.io/how-to-secure-stream-with-jwt-stream-security-filter/
[9] https://learn.microsoft.com/en-us/azure/container-apps/authentication
[10] https://yalantis.com/blog/how-to-develop-a-video-streaming-app-like-hulu/
[11] https://learn.microsoft.com/ja-jp/azure/architecture/example-scenario/serverless/microservices-with-container-apps