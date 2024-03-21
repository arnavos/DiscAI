import os
import cv2
import numpy
import colorama
import json
import datetime
from extenv.paths import CAP_DATA

__config__ = json.loads(CAP_DATA.open("r").read())


class NewChallenge:
    def __init__(self):
        pass

    @staticmethod
    def _load_model(path_model_onnx):
        if (
            not os.path.isfile(path_model_onnx)
            or not path_model_onnx.endswith(".onnx")
            or not os.path.getsize(path_model_onnx)
        ):
            now = datetime.datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            raise RuntimeError(
                f"{colorama.Fore.GREEN}{dt_string}{colorama.Fore.RESET} | {colorama.Fore.BLUE}DEBUG{colorama.Fore.RESET} - >> Unable to load model : {path_model_onnx}"
            )
        return cv2.dnn.readNetFromONNX(path_model_onnx)

    @staticmethod
    def _classify(net, data):
        img_arr = numpy.frombuffer(data, numpy.uint8)
        img = cv2.imdecode(img_arr, flags=1)

        img = cv2.resize(img, (64, 64))
        blob = cv2.dnn.blobFromImage(
            img, 1 / 255.0, (64, 64), (0, 0, 0), swapRB=True, crop=False
        )

        net.setInput(blob)
        out = net.forward()
        if not numpy.argmax(out, axis=1)[0]:
            return True
        return False

    def classify(self, prompt: str, images: list):
        if prompt not in __config__["all_prompts"]:
            now = datetime.datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print(
                f'{colorama.Fore.GREEN}{dt_string}{colorama.Fore.RESET} | {colorama.Fore.BLUE}DEBUG{colorama.Fore.RESET} - >> Unable to load model : {prompt.replace(" ", "_")}.onnx | Untrained'
            )
            return False

        __solutions__ = []

        for image in images:
            __model__ = self._load_model("models/" + __config__[prompt])
            __result__ = self._classify(__model__, image)

            if __result__:
                __solutions__.append(images.index(image))

        return __solutions__
