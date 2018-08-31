import numpy as np

from PIL import Image, ImageDraw, ImageOps
from utils.prompt.selector import Selector


def text_rotate(text_im):
    rotate_d = np.random.randint(-25, 25, size=1)[0]
    rotate_im = text_im.rotate(rotate_d, resample=Image.BICUBIC, expand=1)
    rotate_im = np.asarray(rotate_im)
    mask_idx = np.where(rotate_im > 0)
    y1 = np.min(mask_idx[0])
    y2 = np.max(mask_idx[0])
    x1 = np.min(mask_idx[1])
    x2 = np.max(mask_idx[1])
    return Image.fromarray(rotate_im[y1:y2, x1:x2], mode='L')


class Builder(object):
    """
    提示词图片生成器
    """
    def __init__(self, config):
        """
        生成器初始化
        :param config: 生成器配置参数
        :return:
        """
        self.width = config['width']
        self.height = config['height']
        self.font_color = config['font_color']
        self.space = config['space']
        self.model = ""

        self.selector = Selector(config['font_path'])

    def get_prompt_picture(self, word):

        target_image = Image.new("RGB", (self.width, self.height), (253, 253, 253))
        font = self.selector.get_font()

        for i in range(len(word)):

            if len(word) == 1:
                font_size = np.random.randint(30, 35, size=1)[0]
                rnd_point = (43, 4)
            elif len(word) == 2:
                font_size = np.random.randint(30, 35, size=1)[0]
                rnd_point = (np.random.randint(15+50*i, 50*i+55-font_size+1, 1)[0],
                             np.random.randint(2, 38-font_size+1, 1)[0])
            elif len(word) == 3:
                font_size = np.random.randint(22, 27, size=1)[0]
                rnd_point = (np.random.randint(8+33*i, 33*i+38-font_size+1, 1)[0],
                             np.random.randint(5, 35-font_size+1, 1)[0])
            elif len(word) == 4:
                font_size = np.random.randint(20, 24, size=1)[0]
                rnd_point = (np.random.randint(4+27*i, 27*i+31-font_size+1, 1)[0],
                             np.random.randint(6, 34-font_size+1, 1)[0])
            elif len(word) == 5:
                font_size = np.random.randint(16, 20, size=1)[0]
                rnd_point = (np.random.randint(3+22*i, 22*i+25-font_size+1, 1)[0],
                             np.random.randint(7, 34-font_size+1, 1)[0])
            else:
                font_size = np.random.randint(16, 20, size=1)[0]
                rnd_point = (np.random.randint(3+22*i, 22*i+25-font_size+1, 1)[0],
                             np.random.randint(7, 34-font_size+1, 1)[0])

            f_w, f_h = (font_size, font_size)
            txt_im = Image.new('L', (f_w, f_h))
            d_text = ImageDraw.Draw(txt_im)
            draw_point = (0, 0)
            d_text.text(draw_point, word[i], fill=255, font=font[str(font_size)])
            txt_im = text_rotate(txt_im)
            target_image.paste(ImageOps.colorize(txt_im, (0, 0, 0), self.font_color), rnd_point, txt_im)

        img = np.array(target_image, dtype='uint8')

        return img
