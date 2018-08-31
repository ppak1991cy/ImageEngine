from multiprocessing import Process

from utils.queue import Queue
# builder
from Builder.builder_map import builder_map
from config import BUILDER_PROCESS
# transformer
from Predictor import ImageTransformer
from config import PREDICTOR_SEQ
# uploader
from Uploader import ImageUploader
from config import SAVER_CONFIG

# saver selected
from config import SAVER_LIST

# task structure
from utils.task import TaskInfo


def _run_builder(task_queue, output_queue):

    while True:
        task = task_queue.get()
        pic_type = task.get_type()
        builder_config = task.get_config()
        print("%s building..." % pic_type)
        builder = builder_map[pic_type](output_queue, builder_config)
        builder.run()


def start_builder(task_queue, output_queue):
    """ start builder
        Args:
            1. queue: queue object to which pictures would be pushed
            2. type : type of picture produced
    """
    assert isinstance(task_queue, Queue)  , "Start Builder error: task_queue is invalid"
    assert isinstance(output_queue, Queue), "Start Builder error: output_queue is invalid"

    process_num = BUILDER_PROCESS
    print("builder start with %s process" % process_num)
    for _ in range(process_num):
        p = Process(target=_run_builder,
                    args=(task_queue, output_queue))
        p.start()


def _run_transformer(input_queue, output_queue, predictor_seq, device):
    transformer = ImageTransformer(input_queue, output_queue, predictor_seq, device)
    transformer.run()


def start_transformer(input_queue, output_queue):
    """ start transformer
        Args:
            1. input_queue : queue object from which transformer could get picture info
            2. output_queue: push picture info that has been processed by transformer
    """
    assert isinstance(input_queue, Queue) , "Start Transfromer error: input queue is invalid"
    assert isinstance(output_queue, Queue), "Start Transfromer error: output queue is invalid"

    # TODO: chose device
    device = "cuda"
    predictor_seq = PREDICTOR_SEQ
    p = Process(target=_run_transformer, args=(input_queue, output_queue, predictor_seq, device))
    p.start()


def _run_uploader(input_queue, saver_list, saver_config):
    uploader = ImageUploader(input_queue, saver_list, saver_config)
    uploader.run()


def start_uploader(input_queue):
    assert isinstance(input_queue, Queue), "Start Saver error: queue is invalid"

    saver_list = SAVER_LIST
    saver_config = SAVER_CONFIG
    process_num = SAVER_CONFIG["process"]
    for _ in range(process_num):
        p = Process(target=_run_uploader, args=(input_queue, saver_list, saver_config))
        p.start()


if __name__ == "__main__":
    task_queue = Queue(size=1000)
    picture_queue = Queue(size=1000)
    upload_queue = Queue(size=1000)

    tasks = [TaskInfo("phrasepicture"), TaskInfo("wordpicture"),
             TaskInfo("iconpicture"), TaskInfo("ninepicture")]
    for task in tasks:
        task.set_num(100000)
        task_queue.put(task)

    start_builder(task_queue, picture_queue)
    start_transformer(picture_queue, upload_queue)
    start_uploader(upload_queue)
