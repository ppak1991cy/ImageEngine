from Builder.base import PictureInfo
from Builder.base import Builder
from Builder.nine.selector import NineSelector
from Builder.nine.translate import get_chinese_name
from utils.prompt import PromptBuilder
from config import TEST

import numpy as np
from PIL import Image
import time
import random

# from utils.log import server_logger


class NinePictureInfo(PictureInfo):

    def __init__(self, lang="zh", level=1, mark=""):
        pic_type = "nine" if not TEST else "nine_test"
        super(NinePictureInfo, self).__init__(
            pic_type=pic_type, lang=lang, level=level, mark=mark)


class NineBuilder(Builder):

    def __init__(self, queue, config):
        """ embedding word selector into builder, setting default porperties """

        nine_config = config["ninepicture"]
        super(NineBuilder, self).__init__(queue, nine_config,
                                          selector=NineSelector,
                                          picture_info=NinePictureInfo)
        self.nrow       = self.config["nrow"]
        self.ncol       = self.config["ncol"]
        self.target_num = self.nrow * self.ncol
        self.size       = self.config["size"]
        self.space      = self.config["space"]

        self.prompt_build = PromptBuilder(config["prompt"])

    def select_elements(self, level):
        cls, answer, other = self.selector.get_pictures(level)
        style = self.selector.get_style(level)
        # collect all elements of the picture
        # the answers and others are path of pictures
        elements = dict()
        elements["cls"]       = cls
        elements["answer"]    = answer
        elements["noise"]     = other
        elements["style"]     = style
        return elements

    def process(self, picture_info):

        elements = self.select_elements(picture_info.level)
        picture_info.style       = elements["style"]
        picture_info.prompt_text = elements["cls"]
        picture_info.ans_location, picture_info.source = \
            self._merge_picture(elements["answer"], elements["noise"])

        if picture_info.lang == "zh":
            picture_info.prompt_text = get_chinese_name(picture_info.prompt_text)
            picture_info.prompt = self.prompt_build.get_prompt_picture(picture_info.prompt_text)
        else:
            picture_info.prompt = self.selector.get_prompt_en(picture_info.prompt_text)

    def _merge_picture(self, answer, noise):

        answer_length = len(answer)
        answer_seq = random.sample(range(0, self.target_num), answer_length)
        answer_seq = sorted(answer_seq)
        # transform sequence of answer into 2D location
        answer_loc = [(location // self.ncol + 1, location % self.nrow + 1) for location in answer_seq]

        picture_list = noise
        for i, ans in zip(answer_seq, answer):
            picture_list.insert(i, ans)

        img = self._produce_picture(picture_list)

        return answer_loc, (img - 127.5) / 127.5

    def _produce_picture(self, pic_list):
        """ read files of picture list, and joint them """

        # start = time.time()
        merge_pic = np.ones((self.size[0], self.size[1], 3))
        average_width = 112
        average_height = 112
        x, y = 0, 0
        for pic in pic_list:
            pic = Image.open(pic).convert("RGB").resize((average_width, average_height))
            pic = np.asarray(pic, dtype='float32')
            merge_pic[y:y+average_height, x:x+average_width, :] = pic
            x += average_width + self.space
            if x == self.size[0] + self.space:
                y += average_height + self.space
                x = 0
        img = [merge_pic]
        img = np.array(img, dtype='float32')

        # server_logger.debug("past picture time: %s" % (time.time() - start))
        return img


if __name__ == "__main__":
    from config import BUILDER_CONIG as CONFIG

    from scipy.misc import imsave

    wb = NineBuilder(None, CONFIG)
    for i, pic_info in enumerate(wb.run()):
        img = pic_info.source * 127.5 + 127.5
        img.resize((344, 344, 3))
        imsave("/mnt/%s.jpg" % i, img)
        print(pic_info.prompt_text, "%s.jpg" % i, pic_info.ans_location)
