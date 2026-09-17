import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from geometry_msgs.msg import Pose


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

        ### nedtil her ### og så laver vi pose 

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