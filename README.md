# agent_agora_bitothello

64bitのビットボード表現で実装したシンプルなオセロプログラムです。

## 使い方

```bash
# インストール
pip install -e .

# 対戦を開始
othello
```

盤面は"B"が黒、"W"が白、"."が空白を表します。手番のプレイヤーは `a1` から `h8` の形式で座標を入力してください。

## テスト

```bash
pytest
```
