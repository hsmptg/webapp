from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
from flask import Flask, render_template

# pip install rpi.gpio
import RPi.GPIO as GPIO

class WebApp():
    def __init__(self):
        print("Started WebApp")

        #to disable RuntimeWarning: This channel is already in use
        GPIO.setwarnings(False)

        GPIO.setmode(GPIO.BCM)
        # para usar o LED da placa (GPIO 47), fazer:
        # sudo sh -c "echo gpio >/sys/class/leds/led0/trigger"
        # para repor o comportamento habitual, fazer
        # sudo sh -c "echo mmc0 >/sys/class/leds/led0/trigger"
        GPIO.setup(23, GPIO.OUT)
        GPIO.output(23, GPIO.LOW)
        GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(18, GPIO.BOTH, callback=self.onButton)

        app = Flask(__name__)
        Bootstrap(app)        
        app.config['DEBUG'] = False
        self.socketio = SocketIO(app)
        self.counter = -1
                
        @app.before_first_request
        def initialize():
            print('Called only once, when the first request comes in')
            
        @app.route('/')
        def index():
            print("render index.html")
            return render_template("index2.html", board = "Raspberry Pi")
        
        @self.socketio.on('connect', namespace='/test')
        def test_connect():
            self.counter += 1
            print("Counter= {0}".format(self.counter))
            print('Client connected')
        
        @self.socketio.on('disconnect', namespace='/test')
        def test_disconnect():
            self.counter -= 1
            print("Counter= {0}".format(self.counter))
            print('Client disconnected')
            
        @self.socketio.on('getVersion', namespace='/test')
        def getVersion():
            print('version')

        @self.socketio.on('ledRCtrl', namespace='/test')
        def ledRCtrl(message):
            print(message['led'])
            GPIO.output(23, GPIO.HIGH if message['led'] else GPIO.LOW)
            if GPIO.input(18):
                print('Input was HIGH')
            else:
                print('Input was LOW')

        self.socketio.run(app, host = '0.0.0.0', port = 5001)

    def onButton(self, channel):
        state = False if GPIO.input(18) else True
        print(state)
        self.socketio.emit('but', {'state': state}, namespace='/test')
        #     self.socketio.emit('setVersion', {'version': msg}, namespace='/test')

if __name__ == '__main__':
    gui = WebApp()