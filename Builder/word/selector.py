import os
import time
from PIL import ImageFont
from random import choice, randint

from Builder.base import Selector
from utils.target_lib import StaticWordlib
# from utils.log import server_logger


class WordSelector(Selector):

    def __init__(self, config):
        super(WordSelector, self).__init__(config)
        self.font_path         = config["font_path"]
        self.font_size         = config["font_size"]
        self.target_key        = config["target_key"]
        self.target_extra      = config["target_extra"]
        self.styles            = config["styles"]

        self.wordlib = StaticWordlib(config["word_path"])
        self.font_list = []
        self.character_dict = {}

        self._load_font()
        self._load_character()

    def _load_character(self):
        # start = time.time()
        self.character_dict = self.wordlib.get_target_lib()
        # server_logger.debug("load text time:%s" % (time.time() - start))

    def _load_font(self):
        # start = time.time()
        font_names = os.listdir(self.font_path)
        for font_name in font_names:
            tmp = dict()
            tmp["font_name"] = font_name.split(".")[0]
            for font_size in range(self.font_size[0], self.font_size[1]+1):
                path = "/".join((self.font_path, font_name))
                tmp[str(font_size)] = ImageFont.truetype(path, font_size)
            self.font_list.append(tmp)
        # server_logger.debug("load font time:%s" % (time.time()-start))
        # server_logger.info("font num: %s" % len(self.font_list))

    def get_font(self):
        font_size = randint(self.font_size[0], self.font_size[1])
        font = choice(self.font_list)
        return font[str(font_size)], font["font_name"]

    def get_character(self, difficulty):
        """ get characters which would be pasted into BG picture
            return:
                1. answer characters
                2. noise characters
        """

        r = randint(1, 100)

        word_pro = self.target_key[difficulty]
        word_extra = self.target_extra[difficulty]

        sum = 0
        t = 0
        for t in range(len(word_pro)):
            sum = sum + word_pro[t]
            if sum >= r:
                break
        answer_len = t + 2
        answer = choice(self.character_dict[str(answer_len)])
        min_extra, max_extra = word_extra[t]
        other_len = randint(min_extra, max_extra)
        if other_len == 0:
            other = ""
        else:
            while True:
                other = choice(self.character_dict[str(other_len)])
                inanswer = False
                for c in other:
                    if c in answer:
                        inanswer = True
                        break
                if not inanswer:
                    break

        return answer, other

    def get_style(self, level):
        return choice(self.styles[level])
