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

# db class
from db.db_class import DbConnector

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
fan_email_controller = EmailController('192.168.0.11', '2082991@iotvanier.com', 'd34HqY87m6bL', "Smart Home Fan Control")
light_email_controller = EmailController('192.168.0.11', '2082991@iotvanier.com', 'd34HqY87m6bL', "Smart Home Light Control")

admin_card = "aaaaaaaaaaa"
db_connection = DbConnector(admin_card)

#light level set outside of range of light sensor to start


class LightLevel:
    light_level = -1
    
    def __init__(self,l):
        self.light_level = l
        
lvl = LightLevel(-1)
box_style_dict = {
    'width': '23%',
    'border': '3px solid gray',
    'margin': '25px 1%',
    'height': '450px',
    'background-color' : 'rgba(159, 168, 181, 0.90)',
    'min-width': '270px',
    'position' : 'relative',
    'box-shadow' : '2px 1px 8px 1px rgb(120, 120, 120)'
}

box_name_dict = {
    'border-bottom': '2px solid lightblue',
    'line-height' : '50px',
    'font': 'bold 20px/50px Arial, sans-serif',
    'height': '50px',
    'background-color' : 'rgba(128, 128, 128, 0.2)'
}

box_label_dict = {
    'border-top': '2px solid lightblue',
    'line-height' : '40px',
    'font': 'bold 16px/40px Arial, sans-serif',
    'height': '40px',
    'background-color' : 'rgba(128, 128, 128, 0.2)',
    'width' : '50%',
    'text-align' : 'left',
    'padding' : '0px 10px',
    'position': 'absolute',
    'bottom': '0',
    'left' : '0',
}

box_num_dict = {
    'border-top': '2px solid lightblue',
    'line-height' : '40px',
    'font': 'bold 16px/40px Arial, sans-serif',
    'height': '40px',
    'background-color' : 'rgba(192, 192, 192, 0.2)',
    'width' : '50%',
    'text-align' : 'right',
    'padding' : '0px 10px',
    'position': 'absolute',
    'bottom': '0',
    'right' : '0',
}

layout = html.Div([
        
        # user info
        html.Div([],
            style = {
                'text-align': 'center',
                'padding': '25px',
                'height': '100%',
                'width' : '20%',
                'float': 'left',
                'background-color' : 'black'
            }
        ),

        html.Div([
            #first box for lights
            html.Div([
                html.Div(['Lights Control',
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
                    
                ],
                style = {'float': 'left', 'width' : '100%', 'padding-top' : '25px'}
                ),
                
                html.Div([
                    html.Div(['Light intensity'], style = box_label_dict),
                    html.Div(['Checking...'], id='LightNumber', style = box_num_dict),
                ])
            ], 
                style = box_style_dict | {'float': 'left'}
            ),
            
            # box for fan
            html.Div([
                html.Div(['Fan Control',
                ], 
                style = box_name_dict
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
                    
                style = {'float':'left', 'width' : '100%', 'padding-top': '25px'}
                )
                
                
            ], 
            
            style = box_style_dict| {'float': 'left'}
            ),
            
            html.Div([
                html.Div(['Temperature Detection',
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
                    max=40,
                    min=-40,
                    style={'transform': 'scaleX(0.80) scaleY(0.80)'}
                )], 
                
                style = {'float':'left', 'width' : '100%', 'padding-top': '25px'}
                         
                ),
                
                html.Div([
                    html.Div(['Temperature'], style = box_label_dict),
                    html.Div(['Checking...'], id='TemperatureNumber', style = box_num_dict),
                ])
            ], 
            
            style = box_style_dict | {'float': 'left'}
            ),
            
            html.Div([
                html.Div(['Humidity Detection',
                ], 
                style = box_name_dict
                ),
                
                html.Div([
                    daq.Thermometer(
                        id='humidity',
                        color="orange",
                        value=0,
                        scale={'start':0,'interval':5},
                        max=100,
                        min=-0,
                        style={'transform': 'scaleX(0.80) scaleY(0.80)'}
                    )
                ], 
                
                style = {'float':'right', 'width' : '100%', 'padding-top': '25px'}
                ),
                
                html.Div([
                    html.Div(['Humidity'], style = box_label_dict),
                    html.Div(['Checking...'], id='ThermometerNumber', style = box_num_dict),
                ])
            ], 
            
            style = box_style_dict | {'float': 'left'}
            ),
            
            # to clear all the boxes for background to reach bottom
            html.Div([], 
            className = 'spacer',
            style = {'clear': 'both'}
            )
            
            ],
            
            style={
                'text-align': 'center',
                'padding': '25px',
                'height' : '100%',
                'width' : '80%',
                'float': 'right',
            }
        ),
        
        ],
        style= {            
            'min-width' : '800px',
            'height' : '100%'
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
    if (lvl.light_level < 0):
        return "Checking..."
    else:
        return str(lvl.light_level)
    

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
            if (fan_email_controller.check_email_response() == 1):
                #turn on fan
                message =  "Fan has turned on."
                fan_email_controller.send_email(message)
                fan_email_controller.sent = False
                
                return str(temp) + u'\N{DEGREE SIGN} C', temp, True
            
            elif (fan_email_controller.check_email_response() == 0):
                #keep fan off
                message =  "Fan will remain off."
                fan_email_controller.send_email(message)
                fan_email_controller.sent = False
            
            elif (fan_email_controller.check_email_response() == 2):
                #send another email to say it does not understand.
                message =  "Response not understood. Please answer with 'YES' or 'NO'."
                fan_email_controller.send_email(message)
    
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
#     return str(22) + "%", 22

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("Smarthome/ESP/light")
    client.subscribe("Smarthome/ESP/rfid")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
#     print(msg.topic+" "+str(msg.payload))
    
    if ('light' in msg.topic):
        lvl.light_level = float(str(msg.payload)[2:-1])
    if ('rfid' in msg.topic):
        db_connection.changeUser(str(msg.payload)[2:-1])


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.0.128", 1883, 80)
client.loop_start()
