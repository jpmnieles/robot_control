"""Example Script for Publishing in ROS
"""


import time
import roslibpy


client = roslibpy.Ros(host="BodyNC-NUC", port=9090)
client.run()

if client.is_connected:
    print('ROS Connection Successful')

talker = roslibpy.Topic(client, 
                        name='/hr/actuators/pose',
                        message_type='hr_msgs/TargetPosture')

if client.is_connected:
    talker.publish(roslibpy.Message({'names': ['EyeTurnRight'],
                                     'values': [-0.34]}))
    print('Sending message...')
    time.sleep(1)

talker.unadvertise()

client.terminate()
