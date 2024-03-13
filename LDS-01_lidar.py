#!/usr/bin/env python

import serial
import threading
import matplotlib.pyplot as plt
import math 

class LDS01:

    def __init__(self, port="/dev/ttyUSB0", baudrate=230400, max_distance=4200):
        self.ser = serial.Serial(port, baudrate)
        self.distance_list = [None] * 360 # Initialize distances for 360 degrees
        self.max_distance = max_distance

    def view_scan(self):
        global is_plot, x, y

        while is_plot:
            plt.figure(1)
            plt.cla()
            plt.ylim(-5000, 5000)
            plt.xlim(-5000, 5000)
            plt.scatter(x, y, c='r', s='8')
            plt.pause(0.001)
        
        plt.close("all")

    def scan(self):
        """
        Update the lidar readings and return list.
        """
        try:
            unique_values = 0
            while unique_values < 360:
                result = self.ser.read(42)
                if result[-1] == result[-2]: # Checksum validation
                    base_angle = (result[1] - 160) * 6
                    for m in range(6):
                        angle = base_angle + m
                        if angle < 360: # Prevent indexing beyond the list
                            distance = result[((6 * (m + 1)) + 1)] * 256 + result[((6 * (m + 1)))]
                            if self.distance_list[angle] is None:
                                if distance > self.max_distance:
                                    self.distance_list[angle] = 'nan' # Mark as 'not a number' if greater than max range
                                elif distance > 0:
                                    unique_values += 1
                                    self.distance_list[angle] = distance

                                    if (type(x) is list):
                                        x[angle] = distance * math.cos(math.radians(angle))

                                    if (type(y) is list):
                                        y[angle] = distance * math.sin(math.radians(angle))

                                else:
                                    self.distance_list[angle] = 'nan' # Mark as 'not a number' if distance is non-positive
                             
        except serial.SerialException:
            print("Serial connection error.")
            self.ser.close()

        return self.distance_list
    


if __name__ == "__main__":

    is_plot = True
    x = []
    y = []
    for _ in range(360):
        x.append(0)
        y.append(0)

    lidar = LDS01()

    threading.Thread(target=lidar.view_scan).start()

    while True:
        readings = lidar.scan()

        print(readings)

