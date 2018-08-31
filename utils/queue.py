"""
    The baseic structure is aimed to communicate between different modules
"""
import multiprocessing


class Queue(object):

    def __init__(self, size):
        self.queue = multiprocessing.Queue(maxsize=size)

    def get(self):
        res = self.queue.get(block=True)
        return res

    def put(self, obj):
        res = self.queue.put(obj, block=True)
        return res

    def len(self):
        return self.queue.qsize()


# create instance
task_queue = Queue(size=1000)
picture_queue = Queue(size=1000)
upload_queue = Queue(size=1000)