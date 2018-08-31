import os
import time
from PIL import ImageFont
import random

from Builder.base import Selector
from utils.target_lib import Iconlib
# from utils.log import server_logger
from utils.func import random_pick

class IconSelector(Selector):

    def __init__(self, config):
        super(IconSelector, self).__init__(config)
        self.target_key        = config["target_key"]
        self.target_extra      = config["target_extra"]
        self.styles            = config["styles"]

        self.iconlib = Iconlib(config["icon_path"])
        self.icon_dict = {}

        self._load_icon()

    def _load_icon(self):
        start = time.time()
        self.icon_dict = self.iconlib.get_target_lib()
        # server_logger.debug("load text time:%s" % (time.time() - start))

    def get_icon(self, difficulty):
        """ get icon classes which would be pasted into BG picture
            return:
                1. answer classes
                2. noise classes
        """

        icon_pro = self.target_key[difficulty]
        icon_extra = self.target_extra[difficulty]

        # random pick length of the anwser, the min length is 2
        candidate_num = [2 + i for i in range(len(icon_pro))]
        num_selected = random_pick(candidate_num, icon_pro)
        # random pick length of the other icon according to the range given
        min_extra, max_extra = icon_extra[num_selected - 2]
        num_other = random.randint(min_extra, max_extra)

        # random pick unique classes
        cls_selected = random.sample(self.icon_dict.keys(), num_selected + num_other)
        # distribute classes to answer
        answer_cls = random.sample(cls_selected, num_selected)
        # distribute remainder classes to other
        for a in answer_cls:
            cls_selected.remove(a)
        other_cls = cls_selected

        # choose picture in every class
        answer = list()
        other = list()
        for cls in answer_cls:
            answer.append(random.choice(self.icon_dict[cls]))
        for cls in other_cls:
            other.append(random.choice(self.icon_dict[cls]))

        return answer, other

    def get_style(self, level):
        return random.choice(self.styles[level])