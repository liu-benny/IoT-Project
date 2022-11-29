import dash
from dash import html, Output, Input, callback, dcc
import dash_daq as daq
import dash_bootstrap_components as dbc
import paho.mqtt.client as mqtt
import soundFunction
from datetime import datetime

# email scripts
# from email_func import send, receive

# email class
from email_classes.email_logic import EmailController

#Libraries
import components.DHT11.DHT11 as DHT
import RPi.GPIO as GPIO

from time import sleep
#Disable warnings (optional)
GPIO.setwarnings(False)
#Select GPIO mode
GPIO.setmode(GPIO.BCM)

#Set light - pin 23 as output
light=23
GPIO.setup(light,GPIO.OUT)
#A0
#Set fan pin
fan1=21
fan2=13
fan3=19
GPIO.setup(fan1,GPIO.OUT) 
GPIO.setup(fan2,GPIO.OUT) 
GPIO.setup(fan3,GPIO.OUT) 

#email controller for fan and light
fan_email_controller = EmailController('192.168.0.11', '2082991@iotvanier.com', '***REMOVED***')
light_email_controller = EmailController('192.168.0.11', '2082991@iotvanier.com', '***REMOVED***')

#light level set outside of range of light sensor to start


class LightLevel:
    light_level = -1
    
    def __init__(self,l):
        self.light_level = l
        
lvl = LightLevel(555)
box_style_dict = {
    'width': '45%',
    'border': '3px solid gray',
    'margin': '25px 2.5%',
    'height': '450px',
    'background-color' : 'rgba(3, 138, 255, 0.90)',
    'min-width': '720px',
}

box_name_dict = {
    'border-bottom': '2px solid lightblue',
    'line-height' : '50px',
    'font': 'bold 20px/50px Arial, sans-serif',
    'height': '50px',
    'background-color' : 'rgba(128, 128, 128, 0.2)'
}

layout = html.Div([
    html.Div([
        html.Div(['Lights',
        ], 
        style = box_name_dict
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Light")),
                dbc.ModalBody("Email sent."),
                
            ],
            id="modal",
            is_open=False,
        ),
        html.Div([
            html.I(id='lightbulb',
            className="bi bi-lightbulb-off text-danger",
            style={'font-size': '10rem','width':'500px','padding-top': '60px'}),
            
            daq.BooleanSwitch(
                id='light-switch',
                on=False,
                color='#00EA64',
                style={'transform': 'scaleX(1.00) scaleY(1.00)'}
            ),
            html.H1(id='LightNumber'),
            
        ],
        style = {'float': 'left', 'width' : '100%', 'padding-top' : '25px'}
        ),
    ], 
        style = box_style_dict | {'float': 'left'}
    ),
        
    html.Div([
        html.Div(['Fan',
        ], 
        style = box_name_dict
        ),
        
        html.Div([
        dcc.Interval(id='interval',interval=5 *1000, n_intervals=0),
        daq.Gauge(
            id='temperature',
            color={"gradient":True,"ranges":{"blue":[-40,0],"orange":[0,25],"red":[25,40]}},
            value=0,
            scale={'start':-40,'interval':5},
            label='Temperature',
            max=40,
            min=-40,
            style={'transform': 'scaleX(0.80) scaleY(0.80)'}
        ),
        html.H1(id='TemperatureNumber'),
        ], 
        
        style = {'float':'left', 'width': '33%','padding-top': '25px'}
                 
        ),
        
        html.Div([
        html.I(id='fan',
        className="bi bi-slash-circle",
        style={'font-size': '10rem','width':'30px'}),
        
        daq.BooleanSwitch(
            id='fan-switch',
            on=False,
            color='#00EA64',
            style={'transform': 'scaleX(1.25) scaleY(1.25)'}
        ),
        
        ], 
            
        style = {'float':'left', 'width': '33%','padding-top': '25px'}
        ),
        
        html.Div([
            daq.Thermometer(
                id='humidity',
                color="orange",
                value=0,
                scale={'start':0,'interval':5},
                label='Humidity',
                max=100,
                min=-0,
                style={'transform': 'scaleX(0.80) scaleY(0.80)'}
            ),
            html.H1(id='ThermometerNumber'),
        ], 
        
        style = {'float':'right', 'width': '33%','padding-top': '25px'}
        ),
    ], 
    
    style = box_style_dict| {'float': 'left'}
    ),
    
    html.Div([
        html.Div(['x',
        ], 
        style = box_name_dict
        ),
    ], 
    
    style = box_style_dict | {'float': 'left','clear' : 'left'}
    ),
    
    html.Div([
        html.Div(['x',
        ], 
        style = box_name_dict
        ),
    ], 
    
    style = box_style_dict | {'float': 'left','clear' : 'right'}
    ),
    
    html.Div([], 
    className = 'spacer',
    style = {'clear': 'both'}
    )
    
    ],
    
    style={
        'text-align': 'center',
        'padding': '25px',
        'height' : '100%',
        'min-width' : '800px',
        'overflow-x': 'scroll',
        'background-image': '''linear-gradient(45deg, transparent 20%, blue 25%, transparent 25%),
                      linear-gradient(-45deg, transparent 20%, blue 25%, transparent 25%),
                      linear-gradient(-45deg, transparent 75%, blue 80%, transparent 0),
                      radial-gradient(gray 0px, transparent 0)''',
    'background-size': '30px 30px, 30px 30px',
    }
)
    
    
# callback for LED LightNumber
@callback(
    [Output('lightbulb', 'class'),
     Output('light-switch','on'),
     Output('modal','is_open')],
    [Input('light-switch','on'),
     Input('interval','n_intervals')]
)
def check_light_switch(isOn,interval):
    if isOn == False:
        if (lvl.light_level < 200 and not light_email_controller.sent):
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            light_email_controller.send_email('Light is lower than 200. Turning on lights at: ' + current_time)
            soundFunction.lightOn()
            GPIO.output(light,GPIO.HIGH)
            light_email_controller.sent = True
            print("email sent")
            return f'bi bi-lightbulb-fill text-success', True, True
            
        else:
            GPIO.output(light,GPIO.LOW)
            light_email_controller.sent = False
            soundFunction.lightOff()
            return f'bi bi-lightbulb-off text-danger', False, False
    
    soundFunction.lightOn()
    GPIO.output(light,GPIO.HIGH)
    light_email_controller.sent = False
    return f'bi bi-lightbulb-fill text-success', True, False

@callback(
    Output('LightNumber','children'),
    Input('interval','n_intervals'))
def update_intensity(interval):
    if(lvl.light_level < 0):
        return "Checking light intensity..."
    else:
        return "Current light intensity: " + str(lvl.light_level)
    

# callback for motor
@callback(
    Output('fan','class'),
    Input('fan-switch','on')
)
def check_fan_switch(isOn):
    if isOn == False:
        GPIO.output(fan1,GPIO.LOW)
        GPIO.output(fan2,GPIO.LOW)
        GPIO.output(fan3,GPIO.LOW)
        soundFunction.fan2()
        return f'bi bi-slash-circle text-danger'
    else:
        soundFunction.fan()
        GPIO.output(fan1,GPIO.HIGH)
        GPIO.output(fan2,GPIO.HIGH)
        GPIO.output(fan3,GPIO.LOW)
        
        # allows email to be received again, once manually turning on then turning off in the future
        fan_email_controller.received = False
        
        return f'bi bi-fan text-success'

#callback for temperature
@callback(
    [Output('TemperatureNumber', 'children'),
     Output('temperature','value'),
     Output('fan-switch','on')],
    [Input('interval','n_intervals'),
     Input('fan-switch','on'),
     Input('TemperatureNumber', 'children')]
)
def check_temperature(interval, isOn, displayTemperature):
    temp = DHT.get_temperature()
#     temp = 22
    
    #have to check if fan is on
    if (temp > 22 and not isOn and not fan_email_controller.received):
        if (not fan_email_controller.sent):
            message =  "The current temperature is {temp}. Would you like to turn on the fan?".format(temp=temp)
            fan_email_controller.send_email(message)
            fan_email_controller.sent = True
        else:
            if (fan_email_controller.check_email('YES')):
                #turn on fan
                message =  "Fan has turned on."
                print(message)
                fan_email_controller.send_email(message)
                fan_email_controller.sent = False
                
                return temp, temp, True
            
            elif (fan_email_controller.check_email('NO')):
                #keep fan off
                message =  "Fan will remain off."
                print(message)
                fan_email_controller.send_email(message)
                fan_email_controller.sent = False
            
    return str(temp) + u'\N{DEGREE SIGN} C' , temp, isOn

# callback for humidity
@callback(
    [Output('ThermometerNumber', 'children'),
    Output('humidity','value')],
    [Input('interval','n_intervals'),
    Input('ThermometerNumber','children')]
)
def check_humidity(interval, displayHumidity):
    return DHT.get_humidity(), DHT.get_humidity()
#     return 22

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("IoTlab/ESP")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
#     print(msg.topic+" "+str(msg.payload))
    
    lvl.light_level = float(str(msg.payload)[2:-1])
#     print(lvl.light_level)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.128", 1883, 80)
client.loop_start()
