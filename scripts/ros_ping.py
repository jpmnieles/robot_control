"""Script for Checking ROS Connection
"""


import roslibpy


client = roslibpy.Ros(host="BodyNC-NUC", port=9090)
client.run()

if client.is_connected:
    print('ROS Connection Successful')

client.terminate()
