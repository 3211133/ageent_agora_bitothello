# Agent Agora: Bit Othello

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD Status](https://img.shields.io/github/actions/workflow/status/ten/ageent_agora_bitothello/.github/workflows/main.yml?branch=main)](https://github.com/ten/ageent_agora_bitothello/actions)

> ビットボードと探索アルゴリズムを駆使し、強力な棋力を目指すエージェントベースのオセロシミュレーション環境。

## 概要 (Overview)

Agent Agora: Bit Othelloは、強力なオセロAIを実装・検証するためのPythonプロジェクトです。ビットボードによる高速な盤面操作と、効率的な探索アルゴリズムを組み合わせることで、高い棋力を実現することを目指します。

## 主な機能 (Features)

*   **高速な盤面表現**: ビットボードを採用し、高速な合法手生成と盤面更新を実現。
*   **効率的な探索アルゴリズム**: ミニマックス法とαβ枝刈り法を組み合わせ、深い読みを可能に。
*   **柔軟な評価関数**: 盤面の安定度、石差、行動可能手数を重み付けして盤面を評価。
*   **定石データベース**: 序盤の展開を高速化・安定化させるための定石DBを搭載。
*   **終盤の完全読み**: ゲーム終盤では全幅探索に切り替え、最善手を導き出す。

## なぜこのプロジェクトを作ったか (Motivation)

このプロジェクトは、エージェントベースのアーキテクチャ設計と、古典的なゲームAIにおける探索・評価技術を探求するために開発されました。様々なAIエージェントを競わせ、改善していくためのプラットフォームを提供します。

## インストール (Installation)

`pyproject.toml` が含まれているため、Poetryを利用した環境構築を推奨します。

```bash
# 依存関係をインストール
poetry install

# 仮想環境を有効化
poetry shell
```

## 使い方 (Quick Start)

各種テストを実行することで、システムの動作を確認できます。

```bash
# すべてのテストを実行
pytest
```

## 開発方法 (Development)

開発に協力してくれる方を歓迎します！

1.  リポジトリをフォークし、クローンします。
2.  Poetryを使って依存関係をインストールします。
    ```bash
    poetry install
    ```
3.  コードを編集し、変更後は必ずテストを実行してください。
    ```bash
    pytest
    ```

その他、詳細な開発ガイドラインは `CONTRIBUTING.md` および `DESIGN.md` を参照してください。
プロジェクトのタスク管理や将来の計画については `ROADMAP.md` を確認してください。

## ライセンス (License)

このプロジェクトはMITライセンスです。詳細は `LICENSE` ファイルを参照してください。