""" Build a capture picture composed of the elements which selected by selector """
from Builder.base.selector import Selector

import time
import hashlib
from utils.log import server_logger


_MD5_SUFFIX = "geetest-diao-bao-le"


def _make_name():
    """ A helper for making picture name """

    s = str(time.time()) + _MD5_SUFFIX
    s = s.encode('utf-8')
    md5_obj = hashlib.md5()
    md5_obj.update(s)
    return md5_obj.hexdigest() + ".jpg"


class PictureInfo(object):

    def __init__(self, pic_type, lang="zh", level=1, mark=""):
        """ A structure, which can be delivered in queue, saving picture information """
        # related to picture
        self.name            = _make_name()        # picture name
        self.bg              = None                # original picture
        self.time            = time.time()         # time stamp of picture generation
        self.pic_type        = pic_type            # captcha type
        self.mark            = mark
        # related to captcha
        self.lang            = lang      # language of picture prompt
        self.level           = level     # the level of difficulty
        self.prompt_text     = None      # prompt of captcha
        self.ans_location    = None      # answer location. format: [[[x, y], [w, h]]]
        self.picture         = None      # final captcha picture after processed
        self.prompt          = None      # prompt picture which would be concatenate at bottom of captcha picture
        # about picture reinforcement
        self.source          = None      # normalized numpy matrix of picture
        self.style           = None      # style for style transfer

    def record(self):
        """ Return a dict with the picture infomation uploaded to database """

        result = {
            "name": self.name,
            "pic_type": self.pic_type,
            "path": self.style,
            "style": self.style,
            "lang": self.lang,
            # "level": "l" + str(self.level),
            "level": "l" + str(self.level + 1),
            "answer_text": self.prompt_text,
            "answer_location": self.ans_location,
            "time": self.time,
            "wordlib": self.mark,
            "used": False
        }
        return result


class Builder(object):

    def __init__(self, queue, config, picture_info, selector=Selector):
        self.config = config
        self.selector = selector(self.config)
        self.queue = queue
        self.picture_info = picture_info

        # picture porperties would be covered
        self.lang = config["lang"]
        self.level = config["level"]
        self.mark = config["mark"]

    def run(self):
        """ public method that run the builder """

        server_logger.info("start build picture... ")
        # print("start build picture and character ")
        num = 0
        while num < self.config["target_num"]:
            try:
                picture_info = self.picture_info(lang=self.lang, level=self.level, mark=self.mark)
                self.process(picture_info)
                if picture_info.ans_location:
                    if num % 100 == 0:
                        server_logger.info("%s picture: %s built" % (picture_info.pic_type, num))
                    self.queue.put(picture_info)
                    num += 1
            except Exception as e:
                server_logger.error(e)

    def select_elements(self, level):
        pass

    def process(self, picture_info):
        pass

