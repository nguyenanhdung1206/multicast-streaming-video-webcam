#!/usr/bin/env python
# -*- coding: utf-8 -*-
import cv2
import socket
import base64
import pyaudio
import numpy as np
from threading import Thread, Lock
import pickle
import wave

"""
    File name: tcp-streaming-multicast-server-audio.video.py
    Author: Jäger Cox // jagercox@gmail.com
    Date created: 08/08/2016
    License: MIT
    Python Version: 2.7
    Code guide line: PEP8
"""

__author__ = "Jäger Cox // jagercox@gmail.com"
__created__ = "08/08/2016"
__license__ = "MIT"
__version__ = "0.1"
__python_version__ = "2.7"
__email__ = "jagercox@gmail.com"

# Sockets channels configuration
IP_SERVER = "127.0.0.1"
VIDEO_SERVER_PORT = 11111
AUDIO_SERVER_PORT = 11112
MAX_NUM_CONNECTIONS_LISTENER = 20


# PyAudio configuration
CHUNK = 1024
CHANNELS = 2
RATE = 44100
INPUT = True
FORMAT = pyaudio.paInt16
WIDTH=2

mutex=Lock()

class ConnectionPoolAudio(Thread):
    def __init__(self, ip, port, conn,wf):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.wf=wf
        print ("[+][.audio] New server socket thread started for " + ip + ":" + str(port))

    def run(self):
                    
        while True:
            data = self.wf.readframes(CHUNK)
            self.conn.send(data)
        self.conn.close()
        p.terminate()


class ConnectionPoolVideo(Thread):
    def __init__(self, ip, port, conn, device):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.conn = conn
        self.device = device
        print ("[+][.video] New server socket thread started for " + self.ip +  ":" + str(self.port))

    def run(self):
        try:
            while True:
                mutex.acquire()
                ret, frame = self.device.read()
                mutex.release()
                if ret == False: 
                    break
                data = pickle.dumps(np.array(frame))
                self.conn.send(data)
        except ValueError:
            print ("Connection lost with " + self.ip + ":" + str(self.port))
        self.conn.close()



def tcp_audio_thread():
    wf = wave.open('test.wav', 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    output=True,
                    frames_per_buffer=CHUNK)
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((IP_SERVER, AUDIO_SERVER_PORT))
    connection.listen(MAX_NUM_CONNECTIONS_LISTENER)
    while True:
        (conn, (ip, port)) = connection.accept()
        thread = ConnectionPoolAudio(ip, port, conn,wf)
        thread.start()
    stream.stop_stream()
    stream.close()
    


def tcp_video_thread():
    camera = cv2.VideoCapture('test.mp4')
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind((IP_SERVER, VIDEO_SERVER_PORT))
    connection.listen(MAX_NUM_CONNECTIONS_LISTENER)
    while True:
        (conn, (ip, port)) = connection.accept()
        thread = ConnectionPoolVideo(ip, port, conn, camera)
        thread.start()
    camera.release()


if __name__ == '__main__':
    print ("Starting...")
    thread_audio = Thread(target=tcp_audio_thread)
    thread_video = Thread(target=tcp_video_thread)
    thread_audio.start()
    thread_video.start()
