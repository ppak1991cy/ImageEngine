from config import BUILDER_CONIG
import os

text_path = BUILDER_CONIG["ninepicture"]["text_path"]

zh_path = os.path.join(text_path, "zh")
en_path = os.path.join(text_path, "en")

PIC_TYPE = {}

zh_fp = open(zh_path)
en_fp = open(en_path)

zh_line = zh_fp.readline()[:-1]
en_line = en_fp.readline()[:-1]
num = 0

while zh_line and en_line:
    num += 1
    PIC_TYPE[en_line] = {
        'chinese': zh_line,
        'type_num': num,
    }
    zh_line = zh_fp.readline()[:-1]
    en_line = en_fp.readline()[:-1]


def get_chinese_name(name):
    return PIC_TYPE[name]['chinese']