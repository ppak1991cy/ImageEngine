from Predictor.predictor_map import predictor_map
from Predictor.style_transfer_old.predictor import OldStylePredictor

import numpy as np
from utils.log import server_logger


def add_prompt_picture(output_picture, prompt):
    w, h, t = output_picture.shape

    w_w, w_h, w_t = prompt.shape

    picture = np.zeros(shape=(w + w_w, h, t), dtype=output_picture.dtype)
    picture[0:w, 0:h] = output_picture
    picture[w:w + w_w, 0:w_h] = prompt

    return picture


class ImageTransformer(object):
    """ link predictors by sequence to be a pipe, and provide a public method to run """

    def __init__(self, input_queue, output_queue, predictor_seq, device):

        # TODO: distribute multi-device to diverse predictors
        self.device = device
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.predictor_seq = predictor_seq

        self.predictor_pipe = []

        self._initialize_predictor()

    def run(self):
        """ public method that run the Transformer """

        server_logger.info("start transform picture... ")
        num = 0
        while True:
            picture_info = self.input_queue.get()
            self._transform(picture_info)
            # concatenate picture and prompt
            picture_info.picture = add_prompt_picture(picture_info.picture, picture_info.prompt)

            if num % 100 == 0:
                server_logger.info("transform: num %s" % num)

            self.output_queue.put(picture_info)
            num += 1

    def _initialize_predictor(self):
        for predictor_name in self.predictor_seq:
            obj_info = predictor_map[predictor_name]
            pkg_dir = obj_info["pkg_dir"]
            # produce predictor object, and put it into predictor pipe
            obj = obj_info["predictor"](pkg_dir=pkg_dir, device=self.device)
            self.predictor_pipe.append(obj)

    def _transform(self, picture_info):
        x = picture_info.source.copy()

        for predictor in self.predictor_pipe:
            # input source and related information into diverse predictors
            if isinstance(predictor, OldStylePredictor):
                x = predictor.predict(x, picture_info.style)

        img = x * 127.5 + 127.5
        img = img.astype('uint8')

        picture_info.picture = img

