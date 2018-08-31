"""
    targets be obtained from three kind of sources:
        1. static text(word)
        2. static picture(icon)
        3. text from database(phrase)
"""

import os
import pymongo


class Targetlib(object):

    def __init__(self):
        self.target_lib = {}

        self._load_target()

    def _load_target(self):
        pass

    def get_target_lib(self):
        return self.target_lib


class StaticWordlib(Targetlib):

    def __init__(self, word_path):
        self.word_path = word_path
        super(StaticWordlib, self).__init__()

    def _load_target(self):
        for file_name in os.listdir(self.word_path):
            fn = file_name.split(".")[0]
            self.target_lib[fn] = []
            fp = open("%s/%s" % (self.word_path, file_name), "rb")
            line = fp.readline()
            while line:
                line = line.decode("utf-8")
                line = line[:-1]
                self.target_lib[fn].append(line)
                line = fp.readline()


class MongoWordlib(Targetlib):

    def __init__(self, host, port, db_name="word", collection="valid_word"):
        self.mongo      = pymongo.MongoClient(host=host, port=port)
        self.db_name    = db_name
        self.collection = collection
        super(MongoWordlib, self).__init__()

    def _load_target(self):
        data_base = self.mongo[self.db_name]

        for record in data_base[self.collection].find():
            if not str(record["length"]) in self.target_lib:
                self.target_lib[str(record["length"])] = []
            self.target_lib[str(record["length"])].append(str(record["word"]))


class Iconlib(Targetlib):

    def __init__(self, icon_path):
        self.icon_path = icon_path
        super(Iconlib, self).__init__()

    def _load_target(self):
        for root, subdir, files in os.walk(self.icon_path):
            cls_name = os.path.basename(root)
            for file in files:
                if file.endswith(".png") or file.endswith(".jpg"):
                    if cls_name not in self.target_lib:
                        self.target_lib[cls_name] = []
                    pic_path = os.path.join(root, file)
                    self.target_lib[cls_name].append(pic_path)

