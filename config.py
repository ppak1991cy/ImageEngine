# whether push into test collection
TEST = True
# upload server url
ONLINE = True

if ONLINE:
    UPLOAD_STATUS_URL = ["http://114.215.28.11:8000/get_server_status", "http://122.226.180.213:8000/get_server_status", "http://123.138.241.101:8000/get_server_status"]
    UPLOAD_CHECK_URL = ["http://114.215.28.11:8000/confirm_file", "http://122.226.180.213:8000/confirm_file", "http://123.138.241.101:8000/confirm_file"]
    UPLOAD_URL = ["http://114.215.28.11:8000/upload", "http://122.226.180.213:8000/upload", "http://123.138.241.101:8000/upload"]
    SAVE_PICTURE_INFO_URL = "http://rq.geetestapi.com:8000/saver/clickpictureinfo"
else:
    UPLOAD_STATUS_URL = ["http://10.0.0.10:8000/get_server_status"]
    UPLOAD_CHECK_URL = ["http://10.0.0.10:8000/confirm_file"]
    UPLOAD_URL = ["http://10.0.0.10:8000/upload"]
    SAVE_PICTURE_INFO_URL = "http://10.0.0.10:8001/saver/clickpictureinfo"

# the database of mongoserver saving picture info
MONGO_DB = "gt_resources"


PRIVATEKEY_PATH = "/mnt/old/datu/RSA_keys/priv_key.pem"

# log config
LOG_LEVEL = "INFO"
SERVER_LOG_PATH = '/tmp/gt-pic-maker.log'


# ------------ Builder config ------------ #

# how many processes start to building pictures
BUILDER_PROCESS = 4

BUILDER_CONIG = {
    "wordpicture": {
        # base parameters
        "size"        : (344, 344),  # width, height
        "font_size"   : (40, 50),
        "target_key"  : ([25, 55, 20, 0],
                         [0, 15, 40, 45]),  # The probability of each length within 2 to 5
        "target_extra": (([0, 0], [0, 0], [0, 0], [0, 0]),
                         ([1, 3], [1, 3], [1, 2], [1, 2])),
        "space"       : 10,
        # static files path
        "bg_path"     : "/mnt/old/datu/bg",
        "font_path"   : "/mnt/old/datu/font",
        "word_path"   : "/mnt/old/datu/word",
        # model parameters
        'styles'      : (('abstract', 'cubism6', 'girl2', 'harley1', "owl"),
                         ('abstract', 'cubism6', 'girl2', 'harley1', 'owl')),
        # other info
        "lang"        : "zh",
        "level"       : 0,
        "mark"        : "",
        # num of picture produced
        "target_num"  : 10000,
    },
    "phrasepicture"   : {
        # base parameters
        "size"        : (344, 344),  # width, height
        "font_size"   : (40, 50),
        "target_key"  : ([15, 55, 30, 0],
                         [0, 15, 40, 45]),  # The probability of each length within 2 to 5
        "space"       : 10,
        # static files path
        "bg_path"     : "/mnt/old/datu/bg",
        "font_path"   : "/mnt/old/datu/font",
        # word database url
        "mongo_host"  : "10.0.0.50",
        "mongo_port"  : 27017,
        "db"          : "word",
        "collection"  : "valid_word",
        # model parameters
        'styles'      : (('abstract', 'cubism6', 'girl2', 'harley1', "owl"),
                         ('abstract', 'cubism6', 'girl2', 'harley1', 'owl')),
        # other info
        "lang"        : "zh",
        "level"       : 0,
        "mark"        : "",
        # num of picture produced
        "target_num"  : 10000,
    },
    "ninepicture": {
        'nrow'        : 3,
        'ncol'        : 3,
        "size"        : (344, 344),  # width, height
        "target_key"  : ([15, 55, 30, 0],
                         [0, 15, 40, 45]),  # The probability of each length within 2 to 5
        'bg_path'     : '/mnt/old/datu/nine/all_nine_pictures',
        'text_path'   : '/mnt/old/datu/nine/prompt',
        'prompt_en_path': '/mnt/old/datu/nine/prompt_en',
        'space'       : 4,
        'styles'      : (('abstract', 'starry_night'),
                         ('abstract', 'starry_night')),
        # other info
        "lang"        : "zh",
        "level"       : 0,
        "mark"        : "",
        # num of picture produced
        "target_num"  : 10000,
    },
    "iconpicture": {
        # base parameters
        "size"        : (344, 344),  # width, height
        "icon_size"  : (40, 50),
        "target_key"  : ([15, 55, 30, 0],
                         [0, 15, 40, 45]),  # The probability of each length within 2 to 5
        "target_extra": (([0, 0], [0, 0], [0, 0], [0, 0]),
                         ([1, 3], [1, 3], [1, 2], [1, 2])),
        "space"       : 10,
        # static files path
        "bg_path"     : "/mnt/old/datu/bg",
        "icon_path"   : "/mnt/old/datu/icon",
        # model parameters
        'styles'      : (('abstract', 'cubism6', 'girl2', 'harley1', "owl"),
                         ('abstract', 'cubism6', 'girl2', 'harley1', 'owl')),
        # other info
        "lang"        : "zh",
        "level"       : 0,
        "mark"        : "",
        # num of picture produced
        "target_num"  : 10000,
    },
    # the prompt would be joint at bottom of picture
    "prompt": {
        "width"       : 116,
        "height"      : 40,
        "font_path"   : "/mnt/old/datu/font",
        "font_color"  : (37, 37, 38),
        "space"       : 20,
    },
}

# ----------- Predictor sequence ----------- #

PREDICTOR_SEQ = [
    "style_transfer",
]

# -------------- Saver config -------------- #

SAVER_LIST = [
    "oss_saver",
]

SAVER_CONFIG = {
    "oss_saver": {
        # cn
        "ACCESS_KEY_ID"    : "LTAIEFgYaESBRo0M",
        "ACCESS_KEY_SECRET": "voZESq5cFNqLtoGJ3i4KU5fMqawYbY",
        "BUCKET_NAME"      : "sensebot",
        "ENDPOINT"         : "oss-cn-qingdao.aliyuncs.com",
        # na
        "ACCESS_KEY_ID2": "LTAIEFgYaESBRo0M",
        "ACCESS_KEY_SECRET2": "voZESq5cFNqLtoGJ3i4KU5fMqawYbY",
        "BUCKET_NAME2"      : "sensebot-na",
        "ENDPOINT2"         : "oss-us-east-1.aliyuncs.com",
        "SAVE_INFO_URL"    : SAVE_PICTURE_INFO_URL
    },
    "local_saver": {
        "SAVE_PATH"        : "/mnt/new"
    },
    "process": 5
}

# a mark of the batch of pictures uploaded
MARK = "2018-08-24"
