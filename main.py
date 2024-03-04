import network
import socket
from time import sleep
import tm1637
import machine
from machine import Pin, ADC
import _thread

ssid = 'get_shredded'
password = 'Build_Biz_190_8%'

# Calculate Fahrenheit from Analog read
def get_temp(pin):
    return ((pin.read_u16()*3.3/65535 - 1.25) / 0.005) * 9 / 5 + 32

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(temp, state):
    html = f"""
        <!DOCTYPE html>
        <html>
        <body>
        <p>Pico W Sensor</p>
        <p>Temperature is {temp}</p>
        </body>
        </html>
        """
    return str(html)

def serve(connection):
   #Start a web server
    state = 'OFF'
    #pico_led.off()
    while True:
        # Program waits here for client request
        client = connection.accept()[0]
        temp = get_temp(thermocouple)
        request = client.recv(1024)
        request = str(request)
        print(request)
        html = webpage(temp, state)
        client.send(html)
        client.close()


# Define analog to digital pin
adc_pin = Pin(26, mode=Pin.IN)
thermocouple = ADC(adc_pin)

# Define TM1637 7 segment display object
tm = tm1637.TM1637(clk=Pin(1), dio=Pin(0))

# Flash bEEF
tm.hex(0xbeef)
global temp
temp = 0
sleep(1)
# Scroll temperature on TM1637 display
def scroll_temp():
    while True:
        temp = get_temp(thermocouple)
        tm.scroll(str(int(temp))+'*f')
        sleep(1)
# Start new thread to leave one thread handling 7 segment display
second_thread = _thread.start_new_thread(scroll_temp, ())

# Other thread continues executing code:
try:
    ip = connect()
    conection = open_socket(ip)
    serve(conection)

except KeyboardInterrupt:
    machine.reset()
