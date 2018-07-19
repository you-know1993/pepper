from pepper.framework.abstract import BaseApp
from pepper.framework.naoqi import *
from pepper.framework.asr import GoogleASR
from pepper.framework.face import OpenFace

from pepper import config

import qi


class NaoqiApp(BaseApp):
    def __init__(self):

        self._application = qi.Application([self.__class__.__name__, "--qi-url={}".format(config.NAOQI_URL)])
        self._application.start()

        super(NaoqiApp, self).__init__(
            NaoqiCamera(self._application.session, config.CAMERA_RESOLUTION, config.CAMERA_FRAME_RATE), OpenFace(),
            NaoqiMicrophone(self._application.session, config.NAOQI_MICROPHONE_INDEX), GoogleASR(config.LANGUAGE),
            NaoqiTextToSpeech(self._application.session))