from ultralytics import YOLO
import os
from IPython.display import display, Image
from IPython import display
from roboflow import Roboflow

display.clear_output()
rf = Roboflow(api_key="qU7Tfb8VbFgYrPeB6Twl")
project = rf.workspace("school-qqqed").project("comodity")
version = project.version(1)
dataset = version.download("yolov8")