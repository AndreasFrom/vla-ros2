import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose

from lerobot.policies.smolvla.modeling_smolvla import SmolVLAPolicy
from lerobot.policies.factory import make_pre_post_processors

import torch
from PIL import Image
import torchvision.transforms.functional as TF

# Derefter kører dine normale imports uden fejl:


class VLAWrapper(Node):

    def __init__(self):
        super().__init__('vla_wrapper')

        self.subscription_ = self.create_subscription(
            Image,
            '/camera/camera/color/image_raw',
            self.image_callback,
            10
        )

        self.publisher_ = self.create_publisher(
            Pose,
            '/vla_publisher/pose',
            10
        )

    def create_dummy_pose(self): # Denne her function skal skiftes ud og laves om til at tage data fra VLA og lave en pose ud af det.
        pose = Pose()

        pose.position.x = 0.0
        pose.position.y = 0.0
        pose.position.z = 0.0

        pose.orientation.x = 0.0
        pose.orientation.y = 0.0
        pose.orientation.z = 0.0
        pose.orientation.w = 1.0

        return pose
    
    def image_callback(self, msg):
        self.get_logger().info('Received image message')
        image = msg 
        ### Ufyld VLA kode her ###

        img_tensor = TF.to_tensor(image).to(device)
        
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
        # på sigt  robot = URController(), robot.get_current_positions(), # gripper = GripperController(node) Hvordan får man gripper position
    
        batch = preprocess(frame)
        with torch.inference_mode():
            pred_action = policy.select_action(batch)
            pred_action = postprocess(pred_action)
    
        print("\n--- Forudsagte Gripper Koordinater & Handling ---")
        print("Action shape:", pred_action.shape)
        print("Gripper action (x, y, z, rotation, gripper):", pred_action.cpu().numpy())

        # VLA laver pose some bliver sendt videre til piblisheren 
        pose = self.create_dummy_pose()

        self.publish_pose(vlaPose=pose)

    def publish_pose(self, vlaPose):

        pose = vlaPose

        self.publisher_.publish(pose)
        self.get_logger().info('Publishing pose message: %s' % pose)


def main(args=None):
    rclpy.init(args=args)

    vla_wrapper = VLAWrapper()

    rclpy.spin(vla_wrapper)

    vla_wrapper.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()