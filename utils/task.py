from config import BUILDER_CONIG


# record all type supported
builder_types = list(BUILDER_CONIG.keys())


class TaskInfo(object):

    def __init__(self, pic_type):

        assert pic_type in builder_types, "Task: %s is invalid picture type" % pic_type

        self.pic_type = pic_type
        self.config = BUILDER_CONIG.copy()

    def set_lang(self, lang):
        self.config[self.pic_type]["lang"] = lang

    def set_level(self, level):
        self.config[self.pic_type]["level"] = level

    def set_mark(self, mark):
        assert mark is str(), "Task: mark must be string"
        self.config[self.pic_type]["mark"] = mark

    def set_num(self, num):
        assert type(num) is int, "Task: number must be int"
        self.config[self.pic_type]["target_num"] = num

    def get_config(self):
        return self.config

    def get_type(self):
        return self.pic_type


def push_task_into_queue(task, task_queue):
    task_queue.put(task)