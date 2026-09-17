# Code from https://huggingface.co/kyle0101/ur5-smolvla-pick-cube-project

from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy


# FRA ANTIGRAVITY
import sys
sys.path.insert(0, "/home/charlotte/EIRt/lerobot/src")

import torch
from PIL import Image
import torchvision.transforms.functional as TF
import cv2

import typing
import typing_extensions
import time

if not hasattr(typing, "Self"):
    typing.Self = typing_extensions.Self

# Derefter kører dine normale imports uden fejl:
from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from lerobot.policies.factory import make_pre_post_processors


# Patch for Python 3.14 / draccus kompatibilitet
import draccus.wrappers.field_wrapper
_orig = draccus.wrappers.field_wrapper.FieldWrapper.get_arg_options
def _patched(self):
    opts = _orig(self)
    if "type" in opts and not callable(opts["type"]):
        del opts["type"]
    return opts
draccus.wrappers.field_wrapper.FieldWrapper.get_arg_options = _patched

# 1. Indlæs SmolVLA model og enhed
model_id = "kyle0101/ur5-smolvla-pick-cube-project"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

policy = SmolVLAPolicy.from_pretrained(model_id).to(device).eval()

preprocess, postprocess = make_pre_post_processors(
    policy.config,
    model_id,
    preprocessor_overrides={"device_processor": {"device": str(device)}},
)

# STACK OVERFLOW
# 2. Load video and extract frames
vidcap = cv2.VideoCapture('video1.mp4')
success,image = vidcap.read()

count = 0
length_total = 0
while success:
    start = time.time()
    cv2.imwrite("frame%d.jpg" % count, image)     # save frame as JPEG file      
    success,image = vidcap.read()
    #print('Read a new frame: ', success)

####################
    try:
        # print("frame" + str(count) + ".jpg")
        img = Image.open("frame0.jpg").convert("RGB")
        # img = Image.open("frame" + str(count) + ".jpg").convert("RGB")
        # print("Indlæste" + "frame" + str(count) + ".jpg")
    except FileNotFoundError:
        print("Fil ikke fundet, genererer et syntetisk testbillede...")
        img = Image.new("RGB", (640, 480), color=(128, 128, 128))
        break

    # Konverter PIL Billedet til en PyTorch Tensor [C, H, W] med værdier [0.0, 1.0]
    img_tensor = TF.to_tensor(img).to(device)

    # 3. Opret observation-dictionary med billeder, robot-tilstand og opgave-instruktion
    frame = {
        "task": "Fold the t-shirt",
    }
    print(policy.config.input_features["observation.state"].shape)
    # Tilføj billedet til alle kamera-nøgler
    for cam_key in policy.config.image_features:
        frame[cam_key] = img_tensor

    # Tilføj dummy robot-tilstand (nulpunkter), da der ikke er en fysisk robot tilsluttet
    frame["observation.state"] = torch.zeros(7, device=device)
    # på sigt  robot = URController()
    # robot.get_current_positions()
    # gripper = GripperController(node) Hvordan får man gripper position


    batch = preprocess(frame)
    with torch.inference_mode():
        pred_action = policy.select_action(batch)
        pred_action = postprocess(pred_action)

    print("\n--- Forudsagte Gripper Koordinater & Handling ---")
    print("Action shape:", pred_action.shape)
    print("Gripper action (x, y, z, rotation, gripper):", pred_action.cpu().numpy())
    count += 1
    end = time.time()
    length = end - start
    length_total += length
    # print("Tid for frame " + str(count) + ": " + str(length) + " sekunder")
    # print("FPS: " + str(1/length))

    print("Gennemsnitlig tid pr. frame: " + str(length_total/count) + " sekunder")
    print("Gennemsnitlig tid pr. frame: " + str(1/(length_total/count)) + "Hz")
