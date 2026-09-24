# FRA ANTIGRAVITY
import sys
sys.path.insert(0, "/home/charlotte/EIRt/lerobot/src")

import torch
from PIL import Image
import torchvision.transforms.functional as TF

import typing
import typing_extensions

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
model_id = "lerobot/smolvla_base"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

policy = SmolVLAPolicy.from_pretrained(model_id).to(device).eval()

preprocess, postprocess = make_pre_post_processors(
    policy.config,
    model_id,
    preprocessor_overrides={"device_processor": {"device": str(device)}},
)

# 2. Indlæs et billede fra en fil (eller opret et syntetisk test-billede)
try:
    img = Image.open("Pasted image.png").convert("RGB")
    print("Indlæste Pasted image.png")
except FileNotFoundError:
    print("Fil ikke fundet, genererer et syntetisk testbillede...")
    img = Image.new("RGB", (640, 480), color=(128, 128, 128))

# Konverter PIL Billedet til en PyTorch Tensor [C, H, W] med værdier [0.0, 1.0]
img_tensor = TF.to_tensor(img).to(device)

# 3. Opret observation-dictionary med billeder, robot-tilstand og opgave-instruktion
frame = {
    "task": "pick up the object",
}

# Tilføj billedet til alle kamera-nøgler
for cam_key in policy.config.image_features:
    frame[cam_key] = img_tensor

# Tilføj dummy robot-tilstand (nulpunkter), da der ikke er en fysisk robot tilsluttet
if "observation.state" in policy.config.input_features:
    state_shape = policy.config.input_features["observation.state"].shape
    frame["observation.state"] = torch.zeros(state_shape, device=device)
else:
    frame["observation.state"] = torch.zeros(6, device=device)

# 4. Kør forudsigelse uden at have en fysisk robot
batch = preprocess(frame)
with torch.inference_mode():
    pred_action = policy.select_action(batch)
    pred_action = postprocess(pred_action)

print("\n--- Forudsagte Gripper Koordinater & Handling ---")
print("Action shape:", pred_action.shape)
print("Gripper action (x, y, z, rotation, gripper):", pred_action.cpu().numpy())