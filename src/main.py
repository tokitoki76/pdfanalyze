import os
import re
import fitz
import glob
import json
import argparse
from tqdm import tqdm
from typing import List, Dict, Union
import logging
import logging.config

from utils.TextNormalizer.TextNormalizer import TextNormalizer

# ログ設定ファイルの読み込み
logging.config.fileConfig('logging.conf')

# ロガーの取得
logger = logging.getLogger()

rex = re.compile(r"[\n]+")

def extract_text_from_page(page: fitz.Page) -> str:
    text = rex.sub("", page.get_text())
    return text

def extract_table_from_page(page: fitz.Page) -> List[List[str]]:
    tabs = page.find_tables()
    
    # 少なくとも1つのテーブルが見つかった場合
    if tabs.tables:
        # 最初のテーブルの内容を表示する
        return {"table": [t.extract() for t in tabs]}

def extract_images_from_page(doc: fitz.Document, page: fitz.Page, output_dir: str, page_num: int) -> List[Dict[str, Union[str, int]]]:
    images = page.get_images(full=True)
    image_info_list = []
    pic_num = 0

    for img_index, img in enumerate(images):
        xref = img[0]
        img = doc.extract_image(xref)

        image_filename = f"image_{page_num + 1}_{img_index + 1}.png"
        image_path = os.path.join(output_dir, image_filename)

        with open(image_path, "wb") as image_file:
            image_file.write(img["image"])

        image_info_list.append({"filename": image_filename, "page_num": page_num + 1})

    return image_info_list

def extract_content_from_pdf(pdf_path: str, output_dir: str) -> None:
    logger.info(f"Start extraction : {pdf_path}")
    filename, _ = os.path.splitext(os.path.basename(pdf_path))

    try:
        tp = TextNormalizer(0b0010011101)
    except:
        logger.error(f"Failed to text normalization")
        return

    try:   
        doc = fitz.open(pdf_path)

        result = {"text": {}, "tables": {}, "images": []}

        for page_num in range(doc.page_count):
            page = doc[page_num]

            text_content = extract_text_from_page(page)
            table_content = extract_table_from_page(page)
            image_info = extract_images_from_page(doc, page, os.path.join(output_dir, "images"), page_num)

            if table_content:
                # table_text = "".join(["".join(x) for x in table_content["table"]])
                result["tables"][f"page_{page_num + 1}"] = table_content
            else:
                table_text = ""

            if text_content:
                text_content_list = [tp.clean_text(t) for t in text_content.split("。") if len(t) > 1]
                result["text"][f"page_{page_num + 1}"] = text_content_list

            if image_info:
                result["images"].extend(image_info)

        doc.close()
    except:
        logger.error(f"Failed to open pdf")
        return

    # JSONファイルに結果を保存
    try:
        json_path = os.path.join(output_dir, filename+".json")
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(result, json_file, ensure_ascii=False, indent=2)
    except:
        logger.error(f"Failed to save json")
        return

    logger.info(f"Extraction completed. JSON saved : {json_path}")


def main(input_dir: str, output_dir: str):
    # 出力ディレクトリを作成
    os.makedirs(output_dir, exist_ok=True)

    # 入力ファイルリスト取得
    file_list = glob.glob(input_dir+"/*")

    index = 0
    for index, fl in enumerate(tqdm(file_list)):
        # 入力ファイルチェック
        if not os.path.isfile(fl):
            continue
        _, ext = os.path.splitext(os.path.basename(fl))
        if ext != ".pdf":
            continue

        # 出力ディレクトリ作成
        output_dir_1 = os.path.join(output_dir, str(index))
        os.makedirs(output_dir_1, exist_ok=True)
        os.makedirs(os.path.join(output_dir_1, "images"), exist_ok=True)

        # PDF分析
        extract_content_from_pdf(fl, output_dir_1)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_dir', type=str, required=True)
    parser.add_argument('-o', '--output_dir', type=str, required=True)

    args = parser.parse_args()

    main(args.input_dir, args.output_dir)

