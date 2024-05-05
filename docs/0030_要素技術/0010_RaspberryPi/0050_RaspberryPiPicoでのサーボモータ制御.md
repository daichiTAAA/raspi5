# 調査資料 - Raspberry Pi Picoでのサーボモータ制御方法
&nbsp;
# 作成記録
---
* 作成日時 2024/5/5 野田大一郎
* 更新日時
&nbsp;
# 概要
---
* このドキュメントはRaspberry Pi Picoでのサーボモータ制御方法の調査資料である。
&nbsp;
# 対象読者
---
* このドキュメントはRaspberry Pi Picoでのサーボモータ制御方法を確認したいエンジニア用である。
&nbsp;
# 目的
---
* Raspberry Pi Picoでのサーボモータ制御方法を記載する。
&nbsp;

# 内容
---
# ハードウェア構成
* Raspberry Pi Pico W
* Tower Pro SG90サーボモータ

# Raspberry Pi Pico W ピン配置
![RaspberryPiPicoWPinout](./images/RaspberryPiPicoWPinout.png)

# 制御方法
Raspberry Pi PicoでTower Pro SG90サーボモータを制御するには、以下の手順で行うことができます。

## 1. 配線

SG90サーボモータとPicoを以下のように接続します。

- サーボモータのオレンジ色の信号線をPicoのGPIO 0ピンに接続
- サーボモータの赤い電源線をPicoのVBUS (5V)ピンに接続  
- サーボモータの茶色のGND線をPicoのGNDピンに接続

SG90の動作電圧は4.8V〜6Vなので、Picoの3.3V端子ではなく5V端子を使います。

## 2. プログラム

以下のMicroPythonコードでサーボモータを制御できます。

```python
from machine import Pin, PWM
import utime

pwm = PWM(Pin(0))  # GPIO 0にPWM設定
pwm.freq(50)  # PWM周波数を50Hzに

def servo_write(degrees):
    duty = int((degrees * 9500 / 180) + 2500)
    pwm.duty_u16(duty)

while True:
    servo_write(0)  # 0度の位置に
    utime.sleep(1)
    servo_write(90)  # 90度の位置に  
    utime.sleep(1)
    servo_write(180)  # 180度の位置に
    utime.sleep(1)
```

ポイントは以下の通りです。

- PWM周波数は50Hzに設定[1][4]
- SG90の制御パルス幅は0.5ms〜2.4msなので[4]、これを16ビット(0〜65535)のduty比に変換
- 0度: 0.5ms = 2500/65535、180度: 2.4ms = 12000/65535 より、duty比は角度に比例して2500〜12000の範囲で変化させる[1]

## 3. 動作範囲の調整

SG90の仕様上の動作角度は0〜180度ですが、個体差によっては端まで動かない場合があります。その場合は、servo_write関数内のduty比の計算式を調整します。例えば、

```python 
duty = int((degrees * 8000 / 180) + 3000)  # 例: 0度=3000, 180度=11000
```

のように、係数と切片の値を変更して動作範囲を狭めます。実際に動かして微調整すると良いでしょう。

以上の手順でRaspberry Pi PicoからSG90サーボモータを制御することができます。パルス幅の計算とPWM制御がポイントです。動作角度の調整も忘れずに行いましょう。