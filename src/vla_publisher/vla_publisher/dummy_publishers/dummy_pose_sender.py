import cv2
import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Pose

class DummyPoseSender(Node):

    def __init__(self):
        super().__init__('dummy_pose_sender')

        timer_period = 0.5 

        self.current_frame = 0

        self.publisher_ = self.create_publisher(
            Pose,
            '/robot/current_pose',
            10
        )

        self.timer = self.create_timer(
            timer_period,
            self.publish_pose
        )

    def publish_pose(self):
        msg = Pose()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.position.x = 0.0
        msg.position.y = 0.0
        msg.position.z = 0.0

        msg.orientation.x = 0.0
        msg.orientation.y = 0.0
        msg.orientation.z = 0.0
        msg.orientation.w = 1.0

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'Publishing pose: {self.current_frame}'
        )



def main(args=None):
    rclpy.init(args=args)

    node = DummyPoseSender()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()