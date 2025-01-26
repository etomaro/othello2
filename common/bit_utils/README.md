# bit操作に関する共通関数・tips


1. bit_utils_doc.py
   documentとして関数形式で記載している
2. gosper_hack_calculate_process.py
   gosper's hackの生成順, 処理過程を確認するためにレポートに出力する
   出力先レポート(処理過程): gosper_hack_calculate_process_report/gosper_hack_calculate_process.csv
   出力先レポート(生成順): gosper_hack_calculate_process_report/gosper_hack_calculate_list.csv
3. gosper_hack_with_state_bit.py
   gosper's hackを応用して特定の桁のビットは固定で1とする場合のnCrの指定されたビットが1のビットを全生成する
4. 2の補数.xlsx
   2の補数の考え方を理解するためにまとめられた資料
5. tests/speed_test.py
   gosper's hackの処理速度をcombinationで生成されるtupleを元に最終的にビットとして作成する既存の処理と速度を比較する
   出力先レポート: speed_test_report/speed_test_60_c_{r}.csv | speed_test_60_c_{r}_pypy.csv
   ※ ファイル名の末尾にpypyがついている場合pythonではなくpypyで実行した場合(手動でファイル名を変える必要がある)
