import os
import time
from random import choice
from PIL import ImageFont

# from utils.log import server_logger

class Selector:

    """
    选择器，初始化时候载入所有图片，字体等资源，需要时候随机返回相应资源
    """

    def __init__(self, font_path):
        self.font_path = font_path
        self.font_size = (16, 35)

        self.font_list = []

        self._load_font()

    def _load_font(self):
        """
        载入所有字体
        :return:
        """
        start = time.time()
        font_names = os.listdir(self.font_path)
        for font_name in font_names:
            tmp = {}
            for font_size in range(self.font_size[0], self.font_size[1]):
                path = "/".join((self.font_path, font_name))
                tmp[str(font_size)] = ImageFont.truetype(path, font_size)
            self.font_list.append(tmp)
        # server_logger.debug("load prompt font time:%s" % (time.time()-start))
        # server_logger.info("prompt font num: %s" % len(self.font_list))

    def get_font(self):
        return choice(self.font_list)
