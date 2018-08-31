from Builder.base import PictureInfo
from Builder.base import Builder
from Builder.icon.selector import IconSelector
from config import TEST

from copy import deepcopy
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import cv2
import time
import random

# from utils.log import server_logger
from utils.image_process import text_rotate, color_distinguish, find_bg_, find_hs_



class IconPictureInfo(PictureInfo):

    def __init__(self, lang="zh", level=1, mark=""):
        pic_type = "icon" if not TEST else "icon_test"
        super(IconPictureInfo, self).__init__(
            pic_type=pic_type, lang=lang, level=level, mark=mark)


def load_icon_image(icon_path, size):
    """ load icon image"""

    target_image = Image.new("RGB", (size, size), (0, 0, 0))

    icon_img = Image.open(icon_path).convert("RGBA").copy()

    w, h = icon_img.size
    length = max(w, h)
    w, h = int(w / length * size), int(h / length * size)

    icon_img = icon_img.resize((w, h))
    icon_img = np.asarray(icon_img)[:, :, 3].reshape(h, w, 1)
    icon_img = np.concatenate([icon_img, icon_img, icon_img], 2)
    icon_img = Image.fromarray(icon_img).convert("RGB").copy()

    target_image.paste(icon_img, (0, 0))

    return target_image.convert("L")


def get_prompt_icon(target_icons, width, height, color):
    """ icon prompt """

    target_image = Image.new("RGB", (width, height), (253, 253, 253))

    for i, icon_path in enumerate(target_icons):
        if len(target_icons) == 1:
            font_size = np.random.randint(30, 35, size=1)[0]
            rnd_point = (43, 4)
        elif len(target_icons) == 2:
            font_size = np.random.randint(30, 35, size=1)[0]
            rnd_point = (np.random.randint(15 + 50 * i, 50 * i + 55 - font_size + 1, 1)[0],
                         np.random.randint(2, 38 - font_size + 1, 1)[0])
        elif len(target_icons) == 3:
            font_size = np.random.randint(22, 27, size=1)[0]
            rnd_point = (np.random.randint(8 + 33 * i, 33 * i + 38 - font_size + 1, 1)[0],
                         np.random.randint(5, 35 - font_size + 1, 1)[0])
        elif len(target_icons) == 4:
            font_size = np.random.randint(20, 24, size=1)[0]
            rnd_point = (np.random.randint(4 + 27 * i, 27 * i + 31 - font_size + 1, 1)[0],
                         np.random.randint(6, 34 - font_size + 1, 1)[0])
        elif len(target_icons) == 5:
            font_size = np.random.randint(16, 20, size=1)[0]
            rnd_point = (np.random.randint(3 + 22 * i, 22 * i + 25 - font_size + 1, 1)[0],
                         np.random.randint(7, 34 - font_size + 1, 1)[0])
        else:
            font_size = np.random.randint(16, 20, size=1)[0]
            rnd_point = (np.random.randint(3 + 22 * i, 22 * i + 25 - font_size + 1, 1)[0],
                         np.random.randint(7, 34 - font_size + 1, 1)[0])

        icon_img = load_icon_image(icon_path, 50)

        w, h = icon_img.size
        f_h, f_w = font_size, int(font_size / h * w)
        icon_img = icon_img.resize((f_w, f_h))
        icon_img = text_rotate(icon_img)
        target_image.paste(ImageOps.colorize(icon_img, (0, 0, 0), color), rnd_point, icon_img)

    target_image = np.array(target_image, dtype='uint8')

    return target_image


class IconBuilder(Builder):

    def __init__(self, queue, config):
        """ embedding word selector into builder, setting default porperties """

        icon_config = config["iconpicture"]
        super(IconBuilder, self).__init__(queue, icon_config,
                                          selector=IconSelector,
                                          picture_info=IconPictureInfo)
        self.size = self.config["size"]
        self.space = self.config["space"]

        self.prompt_config = config["prompt"]

    def select_elements(self, level):
        bg              = self.selector.get_bg()
        answer, noise   = self.selector.get_icon(level)
        style           = self.selector.get_style(level)
        # collect all elements of the picture
        elements = dict()
        elements["bg"]        = bg
        elements["answer"]    = answer
        elements["noise"]     = noise
        elements["style"]     = style
        return elements

    def process(self, picture_info):
        elements = self.select_elements(picture_info.level)
        picture_info.bg          = elements["bg"]
        picture_info.style       = elements["style"]
        picture_info.prompt_text = elements["answer"]
        picture_info.ans_location, picture_info.source = \
            self._past_icon(picture_info.bg, elements)

        picture_info.prompt = get_prompt_icon(picture_info.prompt_text,
                                              self.prompt_config["width"],
                                              self.prompt_config["height"],
                                              self.prompt_config["font_color"]
                                              )

    def _past_icon(self, picture, elements):
        start = time.time()
        mask = np.zeros(shape=self.size, dtype=int)

        source_im_cv2 = cv2.resize(picture, self.size)
        process_im_cv2 = deepcopy(source_im_cv2)

        answer_location = []
        icons = elements["answer"] + elements["noise"]
        for k, icon_path in enumerate(icons):
            icon_img = self._produce_icon(icon_path)
            location, mask = self._get_location(picture, mask, self.size[0], self.size[1], icon_img.width,
                                                icon_img.height)
            if not location:
                return None, None
            content_font = source_im_cv2[location[0] - int(icon_img.width/2):location[0] +
                                         int(icon_img.width/2),
                                         location[1] - int(icon_img.height/2):location[1] +
                                         int(icon_img.height/2), :]
            black_2_color = find_hs_(content_font)
            white_2_color = find_bg_(content_font)

            obj = np.array(ImageOps.colorize(icon_img, white_2_color, black_2_color))[:, :, ::-1]
            process_im_cv2 = cv2.seamlessClone(obj, process_im_cv2, 255 * np.ones(obj.shape, obj.dtype), location,
                                               cv2.NORMAL_CLONE)

            if icon_path in elements["answer"]:
                answer_location.append((location, (icon_img.width, icon_img.height)))

        process_im_cv2 = np.array(process_im_cv2, dtype='float32')
        process_im_cv2 = process_im_cv2[:, :, ::-1]

        img = list()
        img.append(process_im_cv2)
        img = np.array(img, dtype='float32')
        # server_logger.debug("past character time: %s" % (time.time()-start))

        return answer_location, (img - 127.5) / 127.5

    def _produce_icon(self, icon_path):
        start = time.time()
        min_size, max_size = self.config["icon_size"]
        size = random.randint(min_size, max_size)

        icon_img = load_icon_image(icon_path, size)
        icon_img = text_rotate(icon_img)

        # server_logger.debug("process character time: %s" % (time.time()-start))
        return icon_img

    def _get_location(self, hsv_pre, mask, s_w, s_h, t_w, t_h):
        count = 0
        while True:
            x = np.random.randint(int(t_w/2) + 5, s_w - 5 - int(t_w/2))
            y = np.random.randint(int(t_h/2) + 5, s_h - 5 - int(t_h/2))
            if np.any(mask[max(0, y-int(t_h/2)-self.space):min(s_h, y+int(t_h/2)+self.space),
                           max(0, x-int(t_w/2)-self.space):min(s_w, x+int(t_w/2)+self.space)]) or \
               color_distinguish(hsv_pre, (x, y), t_w, t_h):
                count += 1
                if count > 2000:
                    return None, None
            else:
                if count < 2000:
                    mask[max(0, y-self.space-int(t_h/2)):min(s_h, y+int(t_h/2)+self.space),
                         max(0, x-int(t_w/2)-self.space):min(s_h, x+int(t_w/2)+self.space)] = 1
                    return (x, y), mask
                else:
                    return None, None


if __name__ == "__main__":
    from config import BUILDER_CONIG as CONFIG

    from scipy.misc import imsave

    wb = IconBuilder(None, CONFIG)
    for i, pic_info in enumerate(wb.run()):
        img = pic_info.source * 127.5 + 127.5
        img.resize((344, 344, 3))
        print(img.shape)
        imsave("/mnt/%s.jpg" % i, img)
