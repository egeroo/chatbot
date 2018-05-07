'''
Created on Apr 3, 2018

@author: Muhammad Ridwan
'''
from server import Server
import sys
import tensorflow as tf

if __name__ == '__main__':
    server = Server()
    server.run()
    
#     local_device_protos = device_lib.list_local_devices()
#     print ([x.name for x in local_device_protos if x.device_type == 'GPU'])
    
#     print (tf.test.gpu_device_name())