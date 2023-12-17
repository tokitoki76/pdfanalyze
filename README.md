# pdfanalyze

## 概要

pymupdfでPDFを分解するサンプルコード  
文章、画像、表データを抽出してjson形式で出力する  

## 依存ライブラリ

mojimoji==0.0.12
PyMuPDF==1.23.7
tqdm==4.65.0

## 実行方法

```
> python -i <input_dir> -o <output_dir>
```

|パラメータ|説明|
|-|-|
|-i/--input_dir|入力ファイル格納ディレクトリパス|
|-o/--output_dir|出力ファイル格納ディレクトリパス|

## 出力

```
{
  "text": {
    "page_1": [
        "・・・"
        "・・・",
        "・・・",
    ],
    "page_2": [
        "・・・"
        "・・・",
        "・・・",
    ]
  },
  "tables": {
    "page_1": {
      "table": [
        ・・・
      ]
    }
  },
  "images": [
    {
      "filename": "image_1_1.png",
      "page_num": 1
    }
  ]
}
```
