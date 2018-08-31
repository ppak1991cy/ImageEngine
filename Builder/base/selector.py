""" Select picture elements from static file or database """

import os
import cv2
import time
from random import choice, randint, sample

# from utils.log import server_logger


class Selector(object):
    """ The base selector loading bg """

    def __init__(self, config):
        self.bg_path = config["bg_path"]
        self.bg_size = config["size"]
        self.bg_list = []

        self._load_bg_list()

    def _load_bg_list(self):
        start = time.time()
        all_bg = os.listdir(self.bg_path)
        for bg_name in all_bg:
            path = os.path.join(self.bg_path, bg_name)
            self.bg_list.append(path)

        # server_logger.debug("load bg time:%s" % (time.time() - start))
        # server_logger.info("bg num: %s" % len(self.bg_list))
        # print("load bg time:%s" % (time.time() - start))
        # print("bg num: %s" % len(self.bg_list))

    def get_bg(self):
        bg_path = choice(self.bg_list)
        bg      = cv2.imread(bg_path)
        bg      = cv2.resize(bg, self.bg_size)
        # bg      = cv2.cvtColor(bg, cv2.COLOR_RGB2BGR)
        return bg


class ClsSelector(object):
    """ The base selector loading bg organized by classes """

    def __init__(self, config):
        # print(config)
        self.bg_path  = config["bg_path"]
        self.bg_size  = config["size"]
        # record pictures path origanized by classes
        self.bg_dict  = {}
        # record all classes
        self.cls_list = []
        # record classes origanized by parents
        self.parent = {}

        self._load_bg_dict()

    def _load_bg_dict(self):
        start = time.time()

        for root, subdir, files in os.walk(self.bg_path):
            if root != self.bg_path:
                self.parent[root] = subdir
            cls_name = os.path.basename(root)
            for file in files:
                if file.endswith(".png") or file.endswith(".jpg"):
                    if cls_name not in self.bg_dict:
                        self.bg_dict[cls_name] = []
                    pic_path = os.path.join(root, file)
                    self.bg_dict[cls_name].append(pic_path)
        self.cls_list = list(self.bg_dict.keys())

        # server_logger.debug("load bg time:%s" % (time.time() - start))
        # server_logger.info("bg cls: %s" % len(self.bg_dict))
        # print("load bg time:%s" % (time.time() - start))
        # print("bg cls: %s" % len(self.bg_dict))

    def get_cls_list(self):
        return self.cls_list.copy()

    def get_cls_bg(self, cls):
        bg_list = self.bg_dict[cls]
        bg_path = choice(bg_list)
        bg = cv2.imread(bg_path)
        bg = cv2.resize(bg, self.bg_size)

        return bg
