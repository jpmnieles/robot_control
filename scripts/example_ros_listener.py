"""Example Script for Listening in ROS
"""


from __future__ import print_function
import roslibpy


client = roslibpy.Ros(host="BodyNC-NUC", port=9090)
client.run()

if client.is_connected:
    print('ROS Connection Successful')

listener = roslibpy.Topic(client,
                          '/hr/actuators/motor_states',
                          'hr_msgs/MotorStateList')

listener.subscribe(lambda message: print(message))

try:
    while True:
        pass
except KeyboardInterrupt:
    listener.unsubscribe()
    client.terminate()
