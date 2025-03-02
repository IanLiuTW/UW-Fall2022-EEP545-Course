#!/usr/bin/env python

import matplotlib.pyplot as plt
import numpy as np
import rospy
import tf
import tf.transformations
from geometry_msgs.msg import (Point, Point32, PointStamped, Polygon,
                               PolygonStamped, Pose, PoseArray, PoseStamped,
                               PoseWithCovarianceStamped, Quaternion)
from std_msgs.msg import Header
from visualization_msgs.msg import Marker


def angle_to_quaternion(angle):
    """Convert an angle in radians into a quaternion _message_."""
    return Quaternion(*tf.transformations.quaternion_from_euler(0, 0, angle))


def quaternion_to_angle(q):
    """Convert a quaternion _message_ into an angle in radians.
    The angle represents the yaw.
    This is not just the z component of the quaternion."""
    x, y, z, w = q.x, q.y, q.z, q.w
    roll, pitch, yaw = tf.transformations.euler_from_quaternion((x, y, z, w))
    return yaw


def rotation_matrix(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.matrix([[c, -s], [s, c]])


def world_to_map(pose, map_info):
    # equivalent to map_to_grid(world_to_map(pose))
    # operates in place
    scale = map_info.resolution
    angle = -quaternion_to_angle(map_info.origin.orientation)
    config = [0.0, 0.0]
    # translation
    config[0] = (1.0 / float(scale)) * (pose[0] - map_info.origin.position.x)
    config[1] = (1.0 / float(scale)) * (pose[1] - map_info.origin.position.y)

    # rotation
    c, s = np.cos(angle), np.sin(angle)
    # we need to store the x coordinates since they will be overwritten
    temp = np.copy(config[0])
    config[0] = int(c * config[0] - s * config[1])
    config[1] = int(s * temp + c * config[1])

    return config


def map_to_world(pose, map_info):
    scale = map_info.resolution
    angle = quaternion_to_angle(map_info.origin.orientation)

    # rotate
    config = np.array([pose[0], map_info.height - pose[1], pose[2]])
    # rotation
    c, s = np.cos(angle), np.sin(angle)
    # we need to store the x coordinates since they will be overwritten
    temp = np.copy(config[0])
    config[0] = c * config[0] - s * config[1]
    config[1] = s * temp + c * config[1]

    # scale
    config[:2] *= float(scale)

    # translate
    config[0] += map_info.origin.position.x
    config[1] += map_info.origin.position.y
    config[2] += angle

    return config
