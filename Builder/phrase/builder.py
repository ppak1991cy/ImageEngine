from Builder.base import PictureInfo
from Builder.base import Builder
from Builder.phrase.selector import PhraseSelector
from utils.prompt import PromptBuilder
from config import TEST

from copy import deepcopy
import numpy as np
from PIL import Image, ImageDraw, ImageOps
import cv2
import time

# from utils.log import server_logger
from utils.image_process import text_rotate, color_distinguish, find_bg_, find_hs_


class PhrasePictureInfo(PictureInfo):

    def __init__(self, lang="zh", level=1, mark=""):
        pic_type = "phrase" if not TEST else "phrase_test"
        super(PhrasePictureInfo, self).__init__(
            pic_type=pic_type, lang=lang, level=level, mark=mark)


class PhraseBuilder(Builder):

    def __init__(self, queue, config):
        """ embedding word selector into builder, setting default porperties """

        phrase_config = config["phrasepicture"]
        super(PhraseBuilder, self).__init__(queue, phrase_config,
                                            selector=PhraseSelector,
                                            picture_info=PhrasePictureInfo)
        self.size = self.config["size"]
        self.space = self.config["space"]

        self.prompt_build = PromptBuilder(config["prompt"])

    def select_elements(self, level):
        bg              = self.selector.get_bg()
        answer, noise   = self.selector.get_character(level)
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
            self._past_character(picture_info.bg, elements)

        picture_info.prompt = self.prompt_build.get_prompt_picture(picture_info.prompt_text)

    def _past_character(self, picture, elements):
        # start = time.time()
        mask = np.zeros(shape=self.size, dtype=int)

        source_im_cv2 = cv2.resize(picture, self.size)
        process_im_cv2 = deepcopy(source_im_cv2)

        answer_location = []
        characters = elements["answer"] + elements["noise"]

        for character in characters:
            character_img = self._produce_character(character)
            location, mask = self._get_location(picture, mask, self.size[0], self.size[1], character_img.width,
                                                character_img.height)
            if not location:
                return None, None
            content_font = source_im_cv2[location[0] - int(character_img.width/2):location[0] +
                                         int(character_img.width/2),
                                         location[1] - int(character_img.height/2):location[1] +
                                         int(character_img.height/2), :]
            black_2_color = find_hs_(content_font)
            white_2_color = find_bg_(content_font)

            obj = np.array(ImageOps.colorize(character_img, white_2_color, black_2_color))[:, :, ::-1]
            process_im_cv2 = cv2.seamlessClone(obj, process_im_cv2, 255 * np.ones(obj.shape, obj.dtype), location,
                                               cv2.NORMAL_CLONE)
            if character in elements["answer"]:
                answer_location.append((location, (character_img.width, character_img.height)))

        process_im_cv2 = np.array(process_im_cv2, dtype='float32')
        process_im_cv2 = process_im_cv2[:, :, ::-1]

        img = []
        img.append(process_im_cv2)
        img = np.array(img, dtype='float32')
        # server_logger.debug("past character time: %s" % (time.time()-start))

        return answer_location, (img - 127.5) / 127.5

    def _produce_character(self, character):
        # start = time.time()
        font, font_name = self.selector.get_font()
        font_w, font_h = font.getsize(character)
        character_img = Image.new('L', (font_w, font_h))
        character_draw = ImageDraw.Draw(character_img)
        character_draw.text((0, 0), character, fill=255, font=font)
        character_img = text_rotate(character_img)
        character_img = character_img.transform((font_w + 20, font_h + 10), Image.AFFINE,
                                                (1, -0.3, 0, -0.1, 1, 0), Image.BILINEAR)

        # server_logger.debug("process character time: %s" % (time.time()-start))
        return character_img

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

    wb = PhraseBuilder(None, CONFIG)
    for i, pic_info in enumerate(wb.run()):
        img = pic_info.source * 127.5 + 127.5
        img.resize((344, 344, 3))
        print(img.shape)
        imsave("/mnt/%s.jpg" % i, img)
