import os
import json
import binascii
from scipy.misc import toimage, imsave
import time

from utils.encryption import generate_sign
from config import MONGO_DB


class Saver(object):

    def __init__(self, config):
        self.save_config = config["local_saver"]
        self.folder_path = self.save_config["SAVE_PATH"]

        self._initlize()

    def _initlize(self):
        if os.path.exists(self.folder_path) is not True:
            os.mkdir(self.folder_path)

        self.pictures_path = os.path.join(self.folder_path, "pictures")
        self.info_path     = os.path.join(self.folder_path, "info")
        if os.path.exists(self.pictures_path) is not True:
            os.mkdir(self.pictures_path)
        if os.path.exists(self.info_path) is not True:
            os.mkdir(self.info_path)

    def save(self, obj):

        try:
            predict_path = os.path.join(self.pictures_path, obj.pic_type)
            info_path = os.path.join(self.info_path, obj.pic_type)

            if not os.path.exists(predict_path):
                os.mkdir(predict_path)
            if not os.path.exists(info_path):
                os.mkdir(info_path)

            picture = toimage(obj.picture, mode="RGB")
            imsave("%s/%s" % (predict_path, obj.name), picture)

            picture_info = obj.record()
            timestamp = time.time()
            message = 'SB' + str(timestamp)
            msg = message.encode('utf-8')
            sign = binascii.b2a_hex(generate_sign(msg))

            data = dict()
            data["db"] = MONGO_DB
            data["timestamp"] = timestamp
            data["sign"] = sign.decode()
            data["picture_infos"] = picture_info
            data["max"] = 100000

            info_file = obj.name.split(".")[0] + "_info"
            info_path = os.path.join(info_path, info_file)
            with open(info_path, "a+") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(e)
            return False
        else:
            return True
