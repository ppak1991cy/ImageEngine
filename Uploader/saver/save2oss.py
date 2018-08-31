import time
import json
import binascii

import oss2
from scipy.misc import toimage
import requests

from utils.encryption import generate_sign
from config import MONGO_DB


class Saver(object):

    def __init__(self, config):

        self.save_config = config["oss_saver"]
        # oss config
        access_key_id = self.save_config["ACCESS_KEY_ID"]
        access_key_secret = self.save_config["ACCESS_KEY_SECRET"]
        endpoint = self.save_config["ENDPOINT"]
        bucket_name = self.save_config["BUCKET_NAME"]

        access_key_id2 = self.save_config["ACCESS_KEY_ID2"]
        access_key_secret2 = self.save_config["ACCESS_KEY_SECRET2"]
        endpoint2 = self.save_config["ENDPOINT2"]
        bucket_name2 = self.save_config["BUCKET_NAME2"]
        # url used to upload picture info
        self.save_pic_info_url = self.save_config["SAVE_INFO_URL"]

        self.cache = []
        self.bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret),
                                  endpoint, bucket_name)
        self.bucket2 = oss2.Bucket(oss2.Auth(access_key_id2, access_key_secret2),
                                  endpoint2, bucket_name2)

    def save(self, obj):

        p = toimage(obj.picture, mode="RGB")
        binary_pic = p.tobytes("jpeg", "RGB")
        try:
            pic_path = "nerualpic/%s/%s" % (obj.style, obj.name)
            self.bucket.put_object(pic_path, binary_pic)
            self.bucket2.put_object(pic_path, binary_pic)
            self.cache.append(obj.record())

            picture_infos = json.dumps(self.cache)
            timestamp = time.time()
            message = 'SB' + str(timestamp)
            msg = message.encode('utf-8')
            sign = binascii.b2a_hex(generate_sign(msg))

            formdata = dict()
            formdata["db"] = MONGO_DB
            formdata["timestamp"] = timestamp
            formdata["sign"] = sign.decode()
            formdata["picture_infos"] = picture_infos
            formdata["max"] = 200000
            response = requests.post(self.save_pic_info_url, data=formdata)
            text = response.text
            if text == "fail":
                # server_logger.error("save picture_info fail")
                print("save picture_info fail")
            self.cache = []

        except oss2.exceptions.OssError:
            # server_logger.warn("upload picture error")
            print("upload picture error")
            return False

        else:
            return True

