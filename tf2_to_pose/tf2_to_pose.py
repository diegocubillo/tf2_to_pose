from geometry_msgs.msg import Pose, PoseStamped

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import ParameterDescriptor

from tf2_ros import TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener


class FrameListener(Node):

    def __init__(self):
        super().__init__('tf2_to_pose_publisher')

        # Declare and acquire parameters
        target_frame_parameter_descriptor = ParameterDescriptor(description='Frame whose pose will be published.')
        self.target_frame = self.declare_parameter(
            'target_frame', 'base_link',target_frame_parameter_descriptor).get_parameter_value().string_value

        source_frame_parameter_descriptor = ParameterDescriptor(description="Observer's frame.")
        self.source_frame = self.declare_parameter(
            'source_frame', 'map',source_frame_parameter_descriptor).get_parameter_value().string_value

        publish_rate_parameter_descriptor = ParameterDescriptor(description='Pose publishing rate.')
        self.publish_rate = self.declare_parameter(
            'publish_rate', 10.0, publish_rate_parameter_descriptor).get_parameter_value().double_value

        use_stamped_parameter_descriptor = ParameterDescriptor(description='Use PoseStamped messages.')
        self.using_stamped = self.declare_parameter(
            'use_stamped', True, use_stamped_parameter_descriptor).get_parameter_value().bool_value
        
        pose_topic_parameter_descriptor = ParameterDescriptor(description='Topic where the pose will be published.')
        self.pose_topic = self.declare_parameter(
            'pose_topic', 'pose', pose_topic_parameter_descriptor).get_parameter_value().string_value

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)


        # Create pose publisher
        if self.using_stamped:
            self.publisher = self.create_publisher(PoseStamped, self.pose_topic, 1)
        else:
            self.publisher = self.create_publisher(Pose, self.pose_topic, 1)


        # Call on_timer function every period
        try:
            self.timer = self.create_timer(1.0/self.publish_rate, self.on_timer)
            self.get_logger().info("Pose publisher created with publish rate %d Hz." % self.publish_rate)
        except ValueError:
            self.get_logger().fatal("Invalid publishing rate. It must be a double.")
            rclpy.shutdown()
            raise


    def on_timer(self):
        # Store frame names in variables that will be used to
        # compute transformations
        from_frame_rel = self.target_frame
        to_frame_rel = self.source_frame

        # Look up for the transformation between target_frame and source_frame
        try:
            t = self.tf_buffer.lookup_transform(
                to_frame_rel,
                from_frame_rel,
                rclpy.time.Time())
        except TransformException as ex:
            self.get_logger().info(
                f'Could not transform "{to_frame_rel}" to "{from_frame_rel}": {ex}')
            return
        if self.using_stamped:
            self.publish_stamped(t)
        else:
            self.publish(t)


    def publish(self, t):
        msg = Pose()
        msg.position.x = t.transform.translation.x
        msg.position.y = t.transform.translation.y
        msg.position.z = t.transform.translation.z
        msg.orientation.x = t.transform.rotation.x
        msg.orientation.y = t.transform.rotation.y
        msg.orientation.z = t.transform.rotation.z
        msg.orientation.w = t.transform.rotation.w
        self.publisher.publish(msg)


    def publish_stamped(self, t):
        msg = PoseStamped()
        msg.header.stamp = super().get_clock().now().to_msg()
        msg.pose.position.x = t.transform.translation.x
        msg.pose.position.y = t.transform.translation.y
        msg.pose.position.z = t.transform.translation.z
        msg.pose.orientation.x = t.transform.rotation.x
        msg.pose.orientation.y = t.transform.rotation.y
        msg.pose.orientation.z = t.transform.rotation.z
        msg.pose.orientation.w = t.transform.rotation.w
        self.publisher.publish(msg)



def main():
    rclpy.init()
    node = FrameListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    rclpy.shutdown()
