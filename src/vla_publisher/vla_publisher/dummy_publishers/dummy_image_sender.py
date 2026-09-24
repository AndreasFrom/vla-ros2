import cv2
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import Image


class DummyImageSender(Node):

    def __init__(self):
        super().__init__('dummy_image_sender')

        self.vidcap = cv2.VideoCapture('/home/andreas/perception_ws/src/vla_publisher/vla_publisher/dummy_publishers/video.mp4')

        if not self.vidcap.isOpened():
            self.get_logger().error('Could not open video.mp4')
            return

        timer_period = 0.5 

        self.current_frame = 0

        self.publisher_ = self.create_publisher(
            Image,
            '/camera/camera/color/image_raw',
            10
        )

        self.timer = self.create_timer(
            timer_period,
            self.publish_image_from_video
        )

    def publish_image_from_video(self):

        success, image = self.vidcap.read()

        if not success:
            self.get_logger().info('End of video reached. Restarting video...')
            self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            return

        msg = Image()

        msg.header.stamp = self.get_clock().now().to_msg()
        msg.height = image.shape[0]
        msg.width = image.shape[1]
        msg.encoding = 'bgr8'
        msg.step = msg.width * 3
        msg.data = image.tobytes()

        self.publisher_.publish(msg)

        self.get_logger().info(
            f'Publishing image frame: {self.current_frame}'
        )

        self.current_frame += 1


def main(args=None):
    rclpy.init(args=args)

    node = DummyImageSender()

    rclpy.spin(node)

    node.vidcap.release()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()