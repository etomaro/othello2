・memory/variables.py
  状態の実際の情報量とarray,ndarrayのメモリ使用量を比較する

  実行方法
    ファイル内のele_num_max, stepを任意の値に変更する
    python research/memory/variables.py

  出力ファイル
    1. [csv]メモリ使用量と実際の情報量とメモリ使用量の差分
      memory/report/variables/memory_{ele_num_max}_{step}.csv
    2. [png]メモリ使用量
      memory/report/variables/memory_{ele_num_max}_{step}.png
    3. [png]実際の情報量とメモリ使用量の差分
      memory/report/variables/diff_{ele_num_max}_{step}.png