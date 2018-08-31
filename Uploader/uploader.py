from Uploader.saver import OssSaver, LocalSaver


saver_map = {
    "oss_saver": OssSaver,
    "local_saver": LocalSaver,
}


class ImageUploader(object):
    """ assemble all saver selected, and provide public method to upload picture """

    def __init__(self, input_queue, saver_list, config):

        self.input_queue = input_queue
        self.saver_list = saver_list
        self.config = config

        self.saver_objs = []

        self._initlize_saver()

    def run(self):
        """ public method for uploading picture """

        while True:
            obj = self.input_queue.get()
            self._upload(obj)

    def _initlize_saver(self):
        for saver_type in self.saver_list:
            if saver_type in saver_map.keys():
                obj = saver_map[saver_type](self.config)
                self.saver_objs.append(obj)
            else:
                print("%s is invalid saver" % saver_type)

    def _upload(self, obj):
        for saver in self.saver_objs:
            saver.save(obj)

