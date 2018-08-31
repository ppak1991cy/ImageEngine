import numpy as np
from PIL import Image
import cv2
from collections import Counter


def text_rotate(text_im):
    rotate_d = np.random.randint(-90, 90)
    rotate_im = text_im.rotate(rotate_d, resample=Image.BICUBIC, expand=1)
    rotate_im = np.asarray(rotate_im)
    mask_idx = np.where(rotate_im > 0)

    y1 = np.min(mask_idx[0])
    y2 = np.max(mask_idx[0])
    x1 = np.min(mask_idx[1])
    x2 = np.max(mask_idx[1])
    return Image.fromarray(rotate_im[y1:y2, x1:x2], mode="L")


def color_distinguish(source_im, paste_point, t_w, t_h):
    source_im = np.asarray(source_im)
    crop_im = source_im[paste_point[1]:paste_point[1] + t_h,
                        paste_point[0]:paste_point[0] + t_w]
    if crop_im[:, :, 2].mean() <= 200:
        return False
    else:
        return True


def find_hs_(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_c = Counter(hsv_img[:, :, 0].flatten())
    if len(h_c) == 1:
        h_value = int(list(h_c.values())[0])
    else:
        h_need = sorted(h_c.values())[int(len(h_c)*0.3):int(len(h_c)*0.8)]
        a = list(filter(lambda x: h_c[x] in h_need, h_c.keys()))
        h_value = int(np.mean(a))
        h_value = (h_value + 60) % 180

    s_max = max(128, hsv_img[:, :, 1].mean())
    v_max = 255 if hsv_img[:, :, 2].mean() < 200 else (hsv_img[:, :, 2].mean()-50)
    color = np.uint8([[[h_value, s_max, v_max]]])
    # print ([hsv_img[:,:,0].mean(), hsv_img[:,:,1].mean(), hsv_img[:,:,2].mean()])
    return list(cv2.cvtColor(color, cv2.COLOR_HSV2RGB)[0][0])


def find_bg_(img):
    gray = img[:, :, 0].mean()*0.299 + img[:, :, 1].mean()*0.587 + img[:, :, 2].mean()*0.114
    if gray < 180:
        return 0, 0, 0
    else:
        return 255, 255, 255