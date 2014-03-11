import spidev
import time
import numpy as np
from threading import Thread
import threading
from Queue import Queue
import socket

HOST = "192.168.1.101"
PORT = 5000
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

spi = spidev.SpiDev()
spi.open(0,0)
numberOfSamplesToAcquire = 12000     # 9000 samples gives about 1 minute of measurement time

ADCdata = []
AcquiringTime = 0

queue = Queue(10)

def get_adc(channel):
    #Perform SPI transaction and store returned bits in 'r'
    r = spi.xfer([1, (8+channel)<<4, 0])
    #Filter data bits from returned bits
    ADCout = ((r[1]&3) << 8) + r[2]
    #Return value from 0-1023
    return ADCout

class ProducerThread(Thread):
    def run(self):
        global queue
        for i in range(numberOfSamplesToAcquire):
            queue.put(get_adc(0))
            time.sleep(0.00579)     # this gives about 150 Hz sample rate
        queue.task_done()
        print 'Producer DONE!'

class ConsumerThread(Thread):
    def run(self):
        global queue

        startTimer = time.time()
        for i in range(numberOfSamplesToAcquire):
            data = queue.get()
            ADCdata.append(data)
            s.sendto(str(data),(HOST,PORT))
        AcquiringTime = (time.time() - startTimer)
        print 'ADC sampling time: ', AcquiringTime
        print 'Number of samples per second:', numberOfSamplesToAcquire/AcquiringTime, '[S/s]'
        print 'Consumer DONE!'

if __name__ == "__main__":
    print 'Starting acquiring', numberOfSamplesToAcquire, 'samples.'
    ProducerThread().start()
    ConsumerThread().start()
    print "Main DONE!"
