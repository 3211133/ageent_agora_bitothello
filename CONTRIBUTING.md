# Othello への貢献 (Contributing)

Othelloプロジェクトへの貢献に興味を持っていただき、ありがとうございます！
私たちは、コミュニティからのあらゆる貢献を歓迎します。

## コミュニケーション

*   **バグ報告や機能提案**: GitHub Issuesをご利用ください。既存のIssueを検索し、重複がないか確認してから起票してください。
*   **質問・相談**: GitHub Discussionsをご利用ください。

## 開発環境のセットアップ

1.  このリポジトリをフォークし、ローカルにクローンします。
    ```bash
    git clone https://github.com/[your-username]/ageent_agora_bitothello.git
    cd ageent_agora_bitothello
    ```
2.  上流リポジトリを`upstream`として登録します。
    ```bash
    git remote add upstream https://github.com/3211133/ageent_agora_bitothello.git
    ```
3.  開発環境をセットアップします。
    ```bash
    ./scripts/dev-setup.sh
    source activate_dev.sh
    ```

## 開発フロー

1.  `main`ブランチから、作業用のブランチを作成します。ブランチ名は`feat/issue-123`や`fix/login-bug`のように、分かりやすい名前を推奨します。
    ```bash
    git checkout -b feat/my-new-feature
    ```
2.  コードを編集します。
3.  コードの品質をチェックします。
    ```bash
    # テストを実行
    ./run_tests.sh
    
    # 構文チェック
    python3 -m py_compile src/othello/*.py
    ```
4.  テストを実行し、すべてのテストがパスすることを確認します。
    ```bash
    # 全テスト実行（カバレッジ付き）
    ./run_tests.sh
    
    # 特定のテストファイルのみ
    ./run_tests.sh tests/test_board.py
    ```
5.  変更内容をコミットします。コミットメッセージは [Conventional Commits](https://www.conventionalcommits.org/) の規約に従うことを推奨します。
    ```bash
    git commit -m "feat: 新機能を追加"
    ```
6.  作業ブランチをプッシュします。
    ```bash
    git push origin feat/my-new-feature
    ```
7.  GitHub上でPull Requestを作成してください。

## コーディング規約

*   **言語**: Python 3.8+ を使用します。
*   **構文チェック**: `python3 -m py_compile` でPython構文の検証を行います。
*   **テスト**: `pytest` を使用し、テストカバレッジ85%以上を維持してください。
*   **ドキュメント**: 重要な関数にはdocstringを記述してください。
*   **セキュリティ**: 入力検証とパストラバーサル対策を適切に実装してください。

## プロジェクト固有のガイドライン

*   **ビットボード操作**: `src/othello/board.py`の設計原則に従ってください。
*   **AI実装**: 新しいAIアルゴリズムは`src/othello/ai.py`に追加し、適切なテストを含めてください。
*   **CLI機能**: CLIの新機能は`src/othello/cli.py`に追加し、エラーハンドリングを適切に実装してください。
*   **ネットワーク機能**: セキュリティ警告を含め、適切な検証を実装してください。

ご協力に感謝します！
