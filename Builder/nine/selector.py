import os
import time
from PIL import ImageFont
from random import choice, randint, sample

from Builder.base import ClsSelector

import scipy.misc
import numpy as np

# from utils.log import server_logger
from utils.func import random_pick


def read_image(path, height, width):
    image = scipy.misc.imread(path, mode='RGB')
    image = scipy.misc.imresize(image, [height, width]) / 255.
    image = np.clip(image, 0, 1)
    image = image[np.newaxis, :height, :width, :]
    image = image.astype('float32')
    return image


class NineSelector(ClsSelector):

    def __init__(self, config):
        super(NineSelector, self).__init__(config)
        self.target_key  = config["target_key"]
        self.total_num   = config["nrow"] * config["ncol"]

        self.styles      = config["styles"]
        # English prompt loaded from static images
        self.prompt_en = {}

        self._load_prompt_en(config["prompt_en_path"])

    def _load_prompt_en(self, prompt_en_path):
        files = os.listdir(prompt_en_path)
        for file in files:
            path = "/".join((prompt_en_path, file))
            self.prompt_en[file.split(".")[0]] = read_image(path, 40, 116)

    def get_prompt_en(self, character):
        """ return English prompt
            called when picture language is 'en'
        """
        return self.prompt_en[character]*255

    def get_pictures(self, level):
        class_list = self.cls_list
        answer_cls = choice(class_list)
        # print(answer_cls)
        num_pro = self.target_key[level]
        candidate_num = [1 + i for i in range(len(num_pro))]
        num_selected = random_pick(candidate_num, num_pro)
        # get path of pictures with answer class
        answer_pic_list = self._get_same_class_pictures(answer_cls, num_selected)

        # delete classes which have same parent with answer class
        cls_list = self._remove_parent_by_cls(answer_cls)
        other_pic_list = self._get_other_pictures(cls_list, self.total_num - num_selected)

        return answer_cls, answer_pic_list, other_pic_list

    def _remove_parent_by_cls(self, cls, cls_list=None):
        if cls_list is None:
            cls_list = self.cls_list.copy()
        for key, items in self.parent.items():
            if cls in items:
                for t in self.parent[key]:
                    cls_list.remove(t)
        return cls_list

    def _get_same_class_pictures(self, cls, num):
        return sample(self.bg_dict[cls], num)

    def _get_other_pictures(self, cls_list, pic_num):
        cls_list = cls_list.copy()
        type_num = randint(2, 4)
        extra_total = pic_num - type_num
        pic_list = []
        for i in range(0, type_num - 1):
            min = extra_total - (type_num-i-1)*3 if extra_total - (type_num-i-1)*3 > 0 else 0
            max = extra_total if extra_total < 3 else 3
            num = randint(min, max)
            extra_total = extra_total - num
            type_name = choice(cls_list)
            pic_list.extend(self._get_same_class_pictures(type_name, num+1))
            cls_list.remove(type_name)
        num = 1 + extra_total
        type_name = choice(cls_list)
        pic_list.extend(self._get_same_class_pictures(type_name, num))
        return pic_list

    def get_style(self, level):
        return choice(self.styles[level])
