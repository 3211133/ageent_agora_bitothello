# オセロゲーム テストスイート

## 概要

このディレクトリには、オセロゲームの盤面処理の正確性を検証するための包括的なテストが含まれています。

## テストファイル構成

### 既存のテストファイル

#### `test_board.py`
- **目的**: 基本的なビットボード操作のテスト
- **内容**:
  - 初期盤面設定の検証
  - 初期状態での合法手生成
  - 基本的な手の適用

#### `test_board_extra.py`
- **目的**: 追加的なボード機能のテスト
- **内容**:
  - 大文字小文字を区別しない手の解析
  - ボードの文字列表現
  - 石の反転計算
  - 無効な文字の処理

#### `test_edge_cases.py`
- **目的**: エッジケースの処理
- **内容**: 境界条件や特殊な状況での動作確認

#### `test_game.py`
- **目的**: ゲーム全体の動作テスト
- **内容**: ゲームロジックの統合テスト

### 新規追加テストファイル

#### `test_board_comprehensive.py` ⭐ NEW
- **目的**: 盤面処理の包括的検証
- **主要テスト**:
  - `test_complex_board_legal_moves()`: 複雑な中盤での合法手生成
  - `test_corner_capture_sequence()`: コーナー取得時の石反転
  - `test_multiple_direction_flips()`: 8方向同時反転
  - `test_edge_wrapping_prevention()`: 盤面端での折り返し防止
  - `test_no_legal_moves_detection()`: 合法手なし状態の検出
  - `test_full_board_no_moves()`: 満局状態の処理
  - `test_long_line_flips()`: 長い直線での石反転
  - `test_board_symmetry()`: 対称盤面での対称性保持
  - `test_occupied_and_empty_consistency()`: 占有/空きマスの整合性
  - `test_move_validation_edge_cases()`: 手の妥当性検証
  - `test_bit_manipulation_accuracy()`: ビット操作の正確性

#### `test_game_integration.py` ⭐ NEW
- **目的**: ゲーム全体の統合テスト
- **主要テスト**:
  - `test_complete_game_sequence()`: 完全なゲーム進行シーケンス
  - `test_undo_redo_consistency()`: アンドゥ/リドゥの整合性
  - `test_pass_scenarios()`: パス状況の処理
  - `test_game_end_detection()`: ゲーム終了条件の検出
  - `test_ai_move_validity()`: AI手の妥当性
  - `test_move_sequence_stone_count()`: 連続手での石数変化
  - `test_alternating_turns()`: 手番の交代
  - `test_board_state_immutability()`: ボード状態の不変性
  - `test_complex_multi_flip_scenario()`: 複雑な多方向反転
  - `test_edge_position_moves()`: 端位置での手
  - `test_performance_stress()`: パフォーマンステスト

#### `test_bitboard_math.py` ⭐ NEW
- **目的**: ビットボード数学的正確性の検証
- **主要テスト**:
  - `test_direction_shifts_accuracy()`: 方向シフトの正確性
  - `test_edge_mask_correctness()`: エッジマスクの正確性
  - `test_bit_position_mapping()`: 座標-ビット位置マッピング
  - `test_bitboard_arithmetic_properties()`: ビットボード算術特性
  - `test_move_flip_mathematics()`: 石反転の数学的正確性
  - `test_legal_moves_algorithm_correctness()`: 合法手アルゴリズムの正確性
  - `test_symmetry_preservation()`: 対称性の保持
  - `test_bitwise_operation_consistency()`: ビット演算の整合性
  - `test_boundary_conditions()`: 境界条件
  - `test_large_number_arithmetic()`: 64ビット算術
  - `test_performance_critical_operations()`: パフォーマンス重要操作

## テスト実行方法

### 個別テスト実行（pytestなし）

```bash
# 基本的な動作確認
python -c "import sys; sys.path.append('src'); from othello.board import BitBoard; print('Import test: OK')"

# 初期盤面テスト
python -c "import sys; sys.path.append('src'); from othello.board import BitBoard; board = BitBoard.initial(); print('Initial board stones:', bin(board.occupied()).count('1'))"

# 合法手テスト
python -c "import sys; sys.path.append('src'); from othello.board import BitBoard; board = BitBoard.initial(); moves = board.legal_moves(board.black, board.white); print('Legal moves:', bin(moves).count('1'))"

# ゲーム統合テスト
python -c "import sys; sys.path.append('src'); from othello.game import Game; from othello.board import parse_move; game = Game(); game.apply_move(parse_move('d3')); print('Game test: OK')"
```

### pytest使用（pytestインストール後）

```bash
# 全テスト実行
pytest tests/ -v

# 特定ファイルのテスト
pytest tests/test_board_comprehensive.py -v
pytest tests/test_game_integration.py -v
pytest tests/test_bitboard_math.py -v

# 特定テスト関数
pytest tests/test_board_comprehensive.py::test_complex_board_legal_moves -v
```

## テストカバレッジ

### 盤面処理の検証項目

✅ **基本操作**
- 初期盤面設定
- 石の配置と反転
- 合法手生成
- 手の適用

✅ **複雑なシナリオ**
- 中盤の複雑な盤面
- 8方向同時反転
- コーナー取得
- 長い直線反転

✅ **エッジケース**
- 盤面端での処理
- 満局状態
- 合法手なし状態
- 孤立石の処理

✅ **数学的正確性**
- ビット演算の正確性
- 座標変換の正確性
- 64ビット算術
- 対称性の保持

✅ **ゲーム統合**
- 完全なゲーム進行
- アンドゥ/リドゥ機能
- AI手の妥当性
- パフォーマンステスト

## 検証された機能

### ビットボード操作
- [x] 方向別シフト演算（8方向）
- [x] エッジマスクによる折り返し防止
- [x] LSB抽出とビットスキャン
- [x] 64ビット整数演算

### 石反転アルゴリズム
- [x] 単方向反転
- [x] 多方向同時反転
- [x] 長距離反転
- [x] 反転石数の正確性

### 合法手生成
- [x] 初期状態（4手）
- [x] 中盤の複雑な状態
- [x] 終盤の制限された状態
- [x] 合法手なし状態の検出

### ゲームロジック
- [x] 手番の交代
- [x] 石数の変化追跡
- [x] ゲーム終了条件
- [x] 状態の不変性

## 発見された問題と修正

### 修正済み問題
1. **GUI相対インポートエラー** - try-except文で解決
2. **ネットワーク機能のエラーハンドリング不足** - 包括的例外処理を追加
3. **パッケージ設定の不備** - pyproject.tomlを修正

### テストで確認された正常動作
- ビットボード演算の数学的正確性
- 石反転アルゴリズムの正確性
- 境界条件での安全な動作
- 大規模データでの安定性

## 今後の拡張可能性

### 追加テスト候補
- [ ] パフォーマンスベンチマーク
- [ ] メモリ使用量テスト
- [ ] 並行処理安全性テスト
- [ ] ファジングテスト

### テスト自動化
- [ ] CI/CD統合
- [ ] カバレッジレポート
- [ ] 回帰テスト自動実行

---

**注意**: pytestが利用できない環境では、各テストファイルの`if __name__ == "__main__"`ブロックを使用して個別実行が可能です。
