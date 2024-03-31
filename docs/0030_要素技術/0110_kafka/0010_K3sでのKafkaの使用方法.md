# 調査資料 - K3sでのKafkaの使用方法の調査
&nbsp;
# 作成記録
---
* 作成日時 2024/3/31 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはK3sでのKafkaの使用方法の調査結果の資料である。
&nbsp;
# 対象読者
---
* このドキュメントはK3sでのKafkaの使用方法の調査結果を確認したいエンジニア用である。
&nbsp;
# 目的
---
* K3sでのKafkaの使用方法の調査結果を記載する。
&nbsp;

# 内容
---
# Kubernetesのマニフェストファイルの使用
## マニフェストファイルとは
マニフェストファイルは、Kubernetesクラスターにデプロイするリソースを定義するためのファイルです。これにより、Kubernetesがどのようなリソースを作成し、どのように管理するかを指定できます。通常、YAML形式で記述され、`kubectl apply`コマンドを使用してクラスターに適用されます。


## マニフェストファイル例（マスターノード１つ、ワーカーノード２つの場合）
### マニフェストの種類
1. Namespace:
   - Namespaceは、Kubernetesクラスタ内の仮想的な分離環境です。
   - リソースを論理的に分離し、名前の衝突を避けるために使用されます。
   - 同じNamespace内のリソースは、名前で簡単に参照できます。
   - Namespaceは通常、アプリケーションやチーム単位で分けられます。

2. StatefulSet:
   - StatefulSetは、ステートフルアプリケーション（状態を持つアプリケーション）をデプロイするために使用されるKubernetesリソースです。
   - 各Podに一意の識別子が割り当てられ、Podの順序と一意性が保証されます。
   - StatefulSetは、Podの安定したネットワーク識別子とストレージを提供します。
   - Kafkaのような分散システムは、StatefulSetを使用してデプロイされることが一般的です。

3. Service:
   - ServiceはKubernetes内のPodへのネットワークアクセスを提供するリソースです。
   - Podは動的にIPアドレスが変更される可能性があるため、Serviceを使ってPodへの安定したアクセス方法を提供します。
   - Serviceは、ラベルセレクターを使用してPodのグループを識別し、それらにトラフィックをルーティングします。

4. ConfigMap: 
    - ConfigMapは、設定情報をKey-Valueペアの形式で保存するためのKubernetesリソースです。
    - アプリケーションの設定ファイル、環境変数、コマンドライン引数などを外部化するために使用されます。
    - Podはボリュームとしてマウントされた ConfigMap を使用して、設定情報にアクセスできます。
    - ConfigMapを使用することで、アプリケーションコードと設定情報を分離できます。
    - ConfigMapを使用する利点:
      1. 設定の外部化: アプリケーションコードから設定情報を分離することで、コードの可読性と保守性が向上します。
      2. 動的な更新: ConfigMapを更新することで、アプリケーションを再デプロイせずに設定を変更できます。
      3. 設定の再利用: 同じConfigMapを複数のPodで共有できるため、設定の一貫性と再利用性が向上します。
      4. シークレット管理: ConfigMapは機密情報の保存には適していませんが、別のリソースであるSecretと組み合わせることで、機密情報も安全に管理できます。

5. Secret:
   - Secretは、パスワード、APIキー、SSL証明書などの機密情報を保存するためのKubernetesオブジェクトです。

分離の是非:
- 一般的に、Namespace、StatefulSet、Service、ConfigMapは別々のマニフェストファイルに分けることが推奨されます。
- 分離することで、各リソースの役割と責任が明確になり、管理がしやすくなります。
- ただし、アプリケーションが小規模で複雑でない場合や、リソース間の関連性が強い場合は、1つのファイルにまとめることもあります。
- 最終的には、アプリケーションの規模、複雑性、およびチームの規約に基づいて判断することが大切です。

### kafka-namespace.yaml
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: kafka
```

### kafka-statefulset.yaml
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
  namespace: kafka
spec:
  serviceName: kafka
  replicas: 3
  podManagementPolicy: Parallel
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - kafka
            topologyKey: kubernetes.io/hostname
      initContainers:
      - name: copy-kafka-secrets
        image: busybox
        command: ['sh', '-c', 'cp -r /etc/kafka/secrets/* /etc/kafka/secrets-data/']
        volumeMounts:
          - name: kafka-secrets
            mountPath: /etc/kafka/secrets
          - name: kafka-secrets-data
            mountPath: /etc/kafka/secrets-data
      containers:
      - name: kafka
        image: confluentinc/cp-kafka:latest
        ports:
        - containerPort: 9092
        - containerPort: 9093
        env:
        - name: KAFKA_BROKER_ID
          value: "1"
        - name: KAFKA_CONTROLLER_QUORUM_VOTERS
          value: "1@kafka-0.kafka:9093,2@kafka-1.kafka:9093,3@kafka-2.kafka:9093"
        volumeMounts:
        - name: config
          mountPath: /etc/kafka
        - name: data
          mountPath: /var/lib/kafka/data
        - name: kafka-secrets-data
          mountPath: /etc/kafka/secrets
        readinessProbe:
          tcpSocket:
            port: 9092
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          tcpSocket:
            port: 9092
          initialDelaySeconds: 30
          periodSeconds: 10
      volumes:
      - name: kafka-secrets-data
        emptyDir: {}
      - name: kafka-secrets
        secret:
          secretName: kafka-secrets
      - name: config
        configMap:
          name: kafka-config
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

### kafka-service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: kafka
  namespace: kafka
spec:
  clusterIP: None
  ports:
    - name: client
      port: 9092
    - name: controller
      port: 9093
  selector:
    app: kafka
```

### kafka-configmap.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kafka-config
  namespace: kafka
data:
  server.properties: |
    broker.id=${KAFKA_BROKER_ID}
    listeners=PLAINTEXT://:9092,CONTROLLER://:9093
    advertised.listeners=PLAINTEXT://${HOSTNAME}:9092
    controller.quorum.voters=${KAFKA_CONTROLLER_QUORUM_VOTERS}
    controller.listener.names=CONTROLLER
    inter.broker.listener.name=PLAINTEXT
    log.dirs=/var/lib/kafka/data
    num.partitions=3
    default.replication.factor=3
    min.insync.replicas=2
    auto.create.topics.enable=false
    delete.topic.enable=true
    num.recovery.threads.per.data.dir=2
    offsets.topic.replication.factor=3
    transaction.state.log.replication.factor=3
    transaction.state.log.min.isr=2
```

### kafka-secrets.yaml
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: kafka-secrets
  namespace: kafka
type: Opaque
data:
  ssl.key: your_keystore_password
  ssl.crt: your_truststore_password
```

&nbsp;

# マニフェストファイルをk3sクラスターにデプロイする方法
マニフェストファイルをKubernetesのマスターノードに作成しデプロイします。

1. マニフェストファイルの作成:

1.1 `kafka-namespace.yaml`ファイルを作成し、内容を追加します。

1.2 `kafka-statefulset.yaml`ファイルを作成し、内容を追加します。

1.3 `kafka-service.yaml`ファイルを作成し、内容を追加します。

1.4 `kafka-configmap.yaml`ファイルを作成し、内容を追加します。

2. マニフェストファイルのデプロイ:

2.1 `kafka-namespace.yaml`をデプロイします。
```
kubectl apply -f kafka-namespace.yaml
```

2.2 `kafka-configmap.yaml`をデプロイします。
```
kubectl apply -f kafka-configmap.yaml
```

2.3 `kafka-statefulset.yaml`をデプロイします。
```
kubectl apply -f kafka-statefulset.yaml
```

2.4 `kafka-service.yaml`をデプロイします。
```
kubectl apply -f kafka-service.yaml
```

3. デプロイメントの確認:

3.1 Kafkaネームスペースのリソースを確認します。
```
kubectl get all -n kafka
```

3.2 StatefulSetのステータスを確認します。
```
kubectl describe statefulset kafka -n kafka
```

3.3 Podのログを確認します。
```
kubectl logs kafka-0 -n kafka
```

これで、提供されたマニフェストファイルがk3sクラスターにデプロイされます。StatefulSetのPodが正常に起動し、Kafkaクラスタが構成されます。

注意: デプロイメントが完了するまでに数分かかる場合があります。また、Kafkaクラスタの適切な動作を確保するために、必要に応じてマニフェストファイルをカスタマイズしてください。

上記の手順に従って、Kafkaクラスタをk3sにデプロイできます。問題がある場合は、エラーメッセージを確認し、適切に対処してください。

&nbsp;

# 問題が生じた場合の対応方法
`kubectl get all -n kafka`の出力のSTATUSが、`CrashLoopBackOff`と表示された場合、Podが繰り返しクラッシュしていることを示しています。

`kubectl logs kafka-0 -n kafka`でログが表示されない場合、Podが起動に失敗していると考えられます。

考えられる原因としては以下のようなものがあります：

1. 設定の問題: `kafka-configmap.yaml`の設定が正しくない可能性があります。例えば、`KAFKA_BROKER_ID`や`KAFKA_CONTROLLER_QUORUM_VOTERS`の値が適切でない可能性があります。

2. ストレージの問題: PersistentVolumeClaimが正常に作成されていない、または必要なストレージが利用可能でない可能性があります。

3. リソースの不足: Kafkaブローカーを実行するために十分なCPUやメモリリソースがない可能性があります。

問題を特定するために、以下の手順を試してください：

1. 1つのPodの詳細な情報を取得します。
```
kubectl describe pod kafka-0 -n kafka
```
これにより、Podが失敗した理由に関する手がかりが得られる可能性があります。

2. PersistentVolumeClaimの状態を確認します。
```
kubectl get pvc -n kafka
```
すべてのPVCが`Bound`状態であることを確認してください。

3. Kafkaブローカーのログを確認します。
```
kubectl logs kafka-0 -n kafka -c kafka
```
`-c kafka`オプションを使用して、Kafkaコンテナのログを表示します。

4. イベントを確認します。
```
kubectl get events -n kafka
```
これにより、Podの失敗に関連するイベントが表示される可能性があります。

これらの手順で得られた情報を基に、Kafkaのステートフルセットが失敗した原因を特定し、適切に対処してください。必要に応じて、マニフェストファイルを修正し、再デプロイしてください。