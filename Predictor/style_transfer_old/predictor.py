from Predictor.style_transfer_old.net import Generator
from Predictor.style_transfer_old.mix_style_info import best_config

import torch
import numpy as np


STYLE_INFO = list(zip(*best_config))[0]


class OldStylePredictor(object):

    def __init__(self, pkg_dir, device="cuda"):
        self.device = device
        self.model = Generator(nb_style=len(STYLE_INFO)).to(device)
        self.model.load_state_dict(torch.load(pkg_dir))

    def predict(self, source, style):

        x_tensor = torch.from_numpy(source.transpose(0, 3, 1, 2))
        x = x_tensor.to(self.device)

        for ind, style_name in enumerate(STYLE_INFO):
            if style_name == style:
                style_coef = np.zeros((1, self.model.nb_style)).astype('float32')
                style_coef[0, ind] = 1
                with torch.no_grad():
                    style_coefficient = torch.from_numpy(style_coef).to(self.device)
                y_style = self.model(x, style_coefficient).detach()
                tensor = y_style.to("cpu")
                tensor = tensor * 127.5 + 127.5
                img = tensor.squeeze(0).clamp(0, 255).numpy()
                img = img.transpose(1, 2, 0).astype('float32')

                # return source normalized
                return (img - 127.5) / 127.5

