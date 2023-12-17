# coding:utf-8
import re
import mojimoji
import unicodedata

re_symbols = re.compile(r"^[\s□■○●*＊・]*")

class TextNormalizer:
    def __init__(self, flag):
        # flagの仕様
        #   bit9   : 数字を削除
        #   bit8   : 数字を0に置き換え
        #   bit7   : カタカナ全角統一
        #   bit6   : カタカナ半角統一
        #   bit5   : 英数字全角統一
        #   bit4   : 英数字半角統一
        #   bit3   : 文頭記号削除
        #   bit2   : html, emailアドレス削除
        #   bit1   : 大文字統一
        #   bit0   : 小文字統一
        #   ※unicode正規化は必ず実施
        self.flag = flag
    
    def clean_text(self, text):
        # unicode正規化は必ず実施
        text = unicodedata.normalize("NFKC", text)

        assert self.flag & 0x0003 != 0x0003, 'bit0/1 are exclusive.'
        if self.flag & 0x0001:    # 小文字に統一
            text = text.lower()
        if self.flag & 0x0002:    # 大文字に統一
            text = text.upper()

        if self.flag & 0x0004:    # htmlタグ、e-mail削除
            text = re.sub(r'(http|https)://[a-zA-z0-9\.\/\?\=\-\+\_\: \@]*', '', text)
            text = re.sub(r'[a-zA-z0-9\.\/\?\=\-\+\_\:]*\@[a-zA-z0-9\.\/\?\=\-\+\_\:]*', '', text)

        if self.flag & 0x0008:    # 記号削除
           text = re_symbols.sub('',text)

        assert self.flag & 0x0030 != 0x0030, 'bit4/5 are exclusive.'
        if self.flag & 0x0010:    # 英数字半角化
            text = mojimoji.zen_to_han(text, kana=False)
        if self.flag & 0x0020:    # 英数字全角化
            text = mojimoji.han_to_zen(text, kana=False)

        assert self.flag & 0x00C0 != 0x00C0, 'bit6/7 are exclusive.'
        if self.flag & 0x0040:    # カタカナ半角化
            text = mojimoji.zen_to_han(text, ascii=False, digit=False)
        if self.flag & 0x0080:    # カタカナ全角化
            text = mojimoji.han_to_zen(text, ascii=False, digit=False)

        assert self.flag & 0x0300 != 0x0300, 'bit8/9 are exclusive.'
        if self.flag & 0x0100:    # 数値を0に置き換え
            text = re.sub(r'[0-9]', '0', text)
            text = re.sub(r'[０-９]', '０', text)
        if self.flag & 0x0200:    # 数字削除
            text = re.sub(r'[0-9０-９]','',text)
            
        return text