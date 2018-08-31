from Predictor.style_transfer_old.predictor import OldStylePredictor


import os


# map predictor type into predict modules and pkg dir
predictor_map = {
    "style_transfer": {
        "predictor": OldStylePredictor,
        "pkg_dir": "/mnt/old/datu/model_pkg/style_transfer_old/iter_220000_weights.pkg",
        "style_list": [
        ]
    }
}
