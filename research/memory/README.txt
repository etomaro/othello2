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

・調査内容
  ・a = list(range(800000000))  # 8億のリスト
    -> 32GBメモリ、6GBのスワップ

    ※ range(n)は遅延型なのでこの時点ではメモリが使用されない。listに変換した際に実際の値が生成される

  ・a = [0xffffffffffffffff] * 4000000000  # 40億のリスト
    -> 32GBメモリ、2GBのスワップ

    multiprocessをする場合の検討
    40億を1/4をつまり75%をMax使用できるとして
    np.array()でほぼ倍になるため半分の20億
    ボードの状態は２つ保持するため半分の10億の状態
    multiprocessing.cpu_count()=16のため16個の並列処理が動かせる。そのため1podあたり6250万個
