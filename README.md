# agent_agora_bitothello

64bitのビットボード表現で実装したシンプルなオセロプログラムです。

## 使い方

```bash
# インストール
pip install -e .

# 対戦を開始
othello [--ai] [--ai-vs-ai] [--ai-level {easy,hard,expert}] [--time-limit SECS] [--host HOST:PORT | --connect HOST:PORT]
# GUI 版を起動
othello-gui
```

GUI では合法手のハイライトと、無効な操作時にメッセージを表示するステータスラベルを追加しています。

`--ai` を指定すると白番をコンピュータが担当します。
`--ai-vs-ai` を指定すると黒白とも自動で進行するデモを閲覧できます。
`--ai-level` で AI の難易度 (`easy`, `hard`, `expert`) を選択できます。`hard` は
最大反転数の手を選び、`expert` では局面の位置評価に基づき手を選ぶため、
`easy` よりも強力です。
`--time-limit` で各プレイヤーの持ち時間（秒）を設定できます。0 を指定すると即時タイムアウトになります。
`--host` で待ち受け、`--connect` で接続してネットワーク対戦が可能です。ホスト側が黒番になります。

## ネットワーク機能

接続メッセージは内部の logger を通して表示されます。

盤面は"B"が黒、"W"が白、"."が空白を表します。手番のプレイヤーは `a1` から `h8` の形式で座標を入力してください。入力中に `u` で一手戻し、`r` でやり直しができます。`s` で盤面を保存し、`l` で保存された盤面を読み込めます。
`BitBoard.from_ascii()` を利用すると、この形式の文字列から盤面オブジェクトを作成できるため、テストやデバッグに便利です。手番入力の解析を行う `parse_move` 関数は `othello.board` にあります。

## Game クラス

`Game` は `BitBoard` と手番情報をまとめて管理する薄いラッパーです。局面の履歴を保持しており、`apply_move()` で着手すると自動で更新されます。`legal_moves()` で合法手集合を取得し、`undo()` / `redo()` で巻き戻しが可能です。CLI から利用する場合は以下のように生成します。

```python
from othello.game import Game
game = Game()  # 初期局面がセットされる
move = parse_move("d3")
game.apply_move(move)
```

## スコアボード

ゲーム終了後の勝敗は `scoreboard.json` に記録され、次回起動時にも累積結果を保持します。
CLI と GUI の両方で対局終了時に現在のスコアボードが表示されます。

## テスト

```bash
pytest
```

## 継続的インテグレーション

GitHub Actions を用いて `pytest` を自動実行します。`main` ブランチへの push または PR 作成時にテストが走ります。
