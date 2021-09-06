#!/usr/bin/env python

import rospy

import rospy
import actionlib

import cv2
from std_msgs.msg import String
from std_msgs.msg import Float64

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

from std_msgs.msg import Float64
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import euler_from_quaternion, quaternion_from_euler


class Behaviour:

    #Subscribing and publishing init
    def __init__(self) -> None:

        #Keeping location points
        self.way_points = {}

        self.way_points["sink_pose"] = [-2.837,-1.963,-3.124]
        self.way_points["center_pose"] = [-2.405,-1.248,1.580]
        self.way_points["exit_pose"] = [-0.008, -1.395,3.094]

        #Init movebase
        self.client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
        self.client.wait_for_server()
        self.goal = MoveBaseGoal()

        #Defining publishers
        self.topic_name = {}
        self.topic_name["camera"] = "/scooopy/camera1/image_raw"
        self.topic_name["blw"] = "/scoopy/blw_revolute_position_controller/command"
        self.topic_name["brw"] = "/scoopy/brw_revolute_position_controller/command"
        #self.topic_name["camera_pan"] = "/scooopy/camera1/image_raw"
        #self.topic_name["camera_tilt"] = "/scooopy/camera1/image_raw"
        self.topic_name["lid"] = "/scoopy/lid_revolute_position_controller/command"
        self.topic_name["mid_arm"] = "/scoopy/mid_inner_slider_position_controller/command"
        self.topic_name["outer_arm"] = "/scoopy/outer_mid_slider_position_controller/command"
        self.topic_name["post_slider"] = "/scoopy/post_slider_position_controller/command"
        self.topic_name["tool_head"] = "/scoopy/toolhead_revolute_position_controller/command"



        self.post_joint = rospy.Publisher(self.topic_name["post_slider"],Float64,queue_size=10)
        self.outer_joint = rospy.Publisher(self.topic_name["outer_arm"],Float64,queue_size=10)
        self.mid_joint = rospy.Publisher(self.topic_name["mid_arm"],Float64,queue_size=10)
        self.lid_joint = rospy.Publisher(self.topic_name["lid"],Float64,queue_size=10)
        self.tool_head_joint = rospy.Publisher(self.topic_name["tool_head"],Float64,queue_size=10)
        
        #self.post_joint = rospy.Publisher(self.topic_name["post_slider"],Float64,queue_size=10)
        #self.post_joint = rospy.Publisher(self.topic_name["post_slider"],Float64,queue_size=10)

        #pub = rospy.Publisher('topic_name', std_msgs.msg.String, queue_size=10)


        #pass
        self.behave()


    def behave(self):
        rospy.loginfo("Setting the robot init pose")
        self.init_pose()
        rospy.loginfo("Moving near to sink")
        self.move_location("sink_pose")
        rospy.loginfo("Completed sink pose movement")
        rospy.sleep(2)
        rospy.loginfo("Moving post slider up")
        self.move_joint("post_slider", 1)
        rospy.sleep(15)
        rospy.loginfo("Completed post slider movement")
        self.init_pose()

        #self.move_location("center_pose")
        #self.move_location("exit_pose")

    def init_pose(self):
        rospy.loginfo("Moving to inital arm configuration")

        self.move_joint("lid", 0)
        rospy.sleep(4)
        self.move_joint("tool_head", -1.6)
        rospy.sleep(4)
        self.move_joint("mid_arm", 0)
        rospy.sleep(4)
        self.move_joint("outer_arm", 0)
        rospy.sleep(4)
        self.move_joint("post_slider", 0)
        rospy.sleep(10)
        rospy.loginfo("Set Robot init pose")


    def move_location(self,location_name):
        rospy.loginfo("Moving into: "+location_name)

        map_coord = self.way_points[location_name]
        self.send_movebase_pose(map_coord[0],map_coord[1],map_coord[2])

    #Sending goal to move base
    def send_movebase_pose(self,x,y,theta):

        self.goal.target_pose.header.frame_id = "map"
        self.goal.target_pose.header.stamp = rospy.Time.now()
        
        self.goal.target_pose.pose.position.x = x
        self.goal.target_pose.pose.position.y = y

        quat = quaternion_from_euler (0, 0,theta)
        self.goal.target_pose.pose.orientation.x = quat[0]
        self.goal.target_pose.pose.orientation.y = quat[1]
        self.goal.target_pose.pose.orientation.z = quat[2]
        self.goal.target_pose.pose.orientation.w = quat[3]


        self.client.send_goal(self.goal)
        wait = self.client.wait_for_result()
        if not wait:
            rospy.logerr("Action server not available!")
            rospy.signal_shutdown("Action server not available!")
        else:
            return self.client.get_result()




    #Moving each joint
    def move_joint(self,name,joint_val):

        if(name == "post_slider"):
            self.post_joint.publish(joint_val)

        elif(name == "outer_arm"):
            self.outer_joint.publish(joint_val)

        elif(name == "mid_arm"):
            self.mid_joint.publish(joint_val)

        elif(name == "lid"):
            self.lid_joint.publish(joint_val)

        elif(name == "tool_head"):
            self.tool_head_joint.publish(joint_val)

    #Return centroid of the detected color
    def detect_object(self,color):
        pass


if __name__ == '__main__':
    try:
        rospy.init_node('scoopy_behave')
        rospy.loginfo("Initializing Scoopy Behaviour")        
        behave_obj = Behaviour()
        

    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation test finished.")