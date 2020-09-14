import asyncio
import time
import websockets
import RPi.GPIO as GPIO  # Importe la bibliothèque pour contrôler les GPIOs
import json

IS_LOCKED = True

GPIO.setmode(GPIO.BOARD)  # Définit le mode de numérotation (Board)
GPIO.setwarnings(False)  # On désactive les messages d'alerte

LED_RED = 29  # Définit le numéro du port GPIO qui alimente la led rouge
LED_GREEN = 31  # Définit le numéro du port GPIO qui alimente la led verte


# Définit la fonction permettant d'allumer une led
def turn_led_on(led):
    GPIO.setup(led, GPIO.OUT)  # Active le contrôle du GPIO
    GPIO.output(led, GPIO.HIGH)  # Allume la led


# Définit la fonction permettant d'éteindre une led
def turn_led_off(led):
    GPIO.setup(led, GPIO.OUT)  # Active le contrôle du GPIO
    GPIO.output(led, GPIO.LOW)  # Eteind la led


# Définit la fonction permettant d'allumer la rouge et éteindre la verte
def turn_red_on():
    turn_led_off(LED_GREEN)  # Eteind la led verte
    turn_led_on(LED_RED)  # Allume la led rouge


# Définit la fonction permettant d'allumer la verte et éteindre la rouge
def turn_green_on():
    turn_led_off(LED_RED)  # Eteind la led rouge
    turn_led_on(LED_GREEN)  # Allume la led verte


# Récupération du serial unique
def get_serial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
    except:
        cpuserial = "ERROR000000000"
    return cpuserial


def open_lock():
    print('The lock is open.')
    turn_green_on()

    global IS_LOCKED
    IS_LOCKED = False
    return IS_LOCKED


def close_lock():
    print('The lock is closed.')
    turn_red_on()

    global IS_LOCKED
    IS_LOCKED = True
    return IS_LOCKED


# Configuration de la connexion websocket
async def connect_wss():
    # url = "wss://rapid-zippy-parcel.glitch.me"
    url = "ws://192.168.1.19:12730"
    async with websockets.connect(url) as websocket:
        close_lock()
        await websocket.send(json.dumps({'connection': {'serial': get_serial(), 'isLocked': IS_LOCKED}}))
        recv = await websocket.recv()

        if recv:
            print(recv)

        while True:
            order = await websocket.recv()

            if order == get_serial() + ' open':
                open_lock()
                await websocket.send(json.dumps({'state': {'serial': get_serial(), 'isLocked': IS_LOCKED}}))
            elif order == get_serial() + ' close':
                close_lock()
                await websocket.send(json.dumps({'state': {'serial': get_serial(), 'isLocked': IS_LOCKED}}))
            else:
                print('Invalid order received.')


def websocket_connection():
    asyncio.get_event_loop().run_until_complete(connect_wss())


def websocket_connection_retry():
    connected = False

    print("Connection lost... reconnecting")

    while not connected:
        # attempt to reconnect, otherwise sleep for 2 seconds  
        try:
            websocket_connection()
            connected = True
            print("Re-connection successful")
        except ConnectionRefusedError:
            print("Connection lost... reconnecting")
            time.sleep(2)
        except websockets.exceptions.ConnectionClosedError:
            print("Connection lost... reconnecting")
            time.sleep(2)
        except websockets.exceptions.InvalidStatusCode:
            print("Connection lost... reconnecting")
            time.sleep(2)


if __name__ == "__main__":
    try:
        websocket_connection()
    except websockets.exceptions.ConnectionClosedError as e:
        websocket_connection_retry()
    except Exception as e:
        print(e)
