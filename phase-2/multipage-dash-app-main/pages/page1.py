import dash
from dash import html, Output, Input, callback, dcc
import dash_daq as daq
import dash_bootstrap_components as dbc

# email scripts
from email_func import send, receive

# Replace libraries by fake ones
import sys
import fake_rpi

sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO # Fake GPIO
sys.modules['smbus'] = fake_rpi.smbus # Fake smbus (I2C)


#Libraries
#import components.DHT11.DHT11 as DHT
import RPi.GPIO as GPIO

from time import sleep
#Disable warnings (optional)
GPIO.setwarnings(False)
#Select GPIO mode
GPIO.setmode(GPIO.BCM)

#Set light - pin 23 as output
light=19
GPIO.setup(light,GPIO.OUT)                                                         

#Set fan pin
fan=21
GPIO.setup(fan,GPIO.OUT) 

#bool for fan and email sent
emailSent=False

box_style_dict = {
    'width': '45%',
    'border': '3px solid gray',
    'margin': '2.5%',
    'height': '400px'
}

layout = html.Div([
    html.Div([
        html.Div([
            html.I(id='lightbulb',
            className="bi bi-lightbulb",
            style={'font-size': '10rem','width':'500px','padding-top': '70px'}),
            
            daq.BooleanSwitch(
                id='light-switch',
                on=True,
                color='#00EA64',
                style={'transform': 'scaleX(1.25) scaleY(1.25)'}
            ),
            
        ],
        style = {'float': 'left', 'width' : '100%', 'padding-top' : '50px'}
        ),
    ], 
            
        style = box_style_dict | {'float': 'left'}
    ),
        
    html.Div([
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
        ], 
        
        style = {'float':'left', 'width': '33%','padding-top': '50px'}
                 
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
            
        style = {'float':'left', 'width': '33%','padding-top': '50px'}
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
            )
        ], 
        
        style = {'float':'right', 'width': '33%','padding-top': '50px'}
        ),
    ], 
    
    style = box_style_dict| {'float': 'right'}
    ),
    
    html.Div([
    ], 
    
    style = box_style_dict | {'float': 'left','clear' : 'left'}
    ),
    
    html.Div([
    ], 
    
    style = box_style_dict | {'float': 'right','clear' : 'right'}
    )
    
    ],
    
    style={
        'text-align': 'center',
        'padding': '25px'
    }
)
    
    
# callback for LED
@callback(
    Output('lightbulb', 'class'),
    Input('light-switch','on')
)
def check_light_switch(isOn):
    if isOn == False:
        GPIO.output(light,GPIO.LOW)
        return f'bi bi-lightbulb-off text-danger'
    else:
        GPIO.output(light,GPIO.HIGH)
        return f'bi bi-lightbulb-fill text-success'


# callback for motor
@callback(
    Output('fan','class'),
    Input('fan-switch','on')
)
def check_fan_switch(isOn):
    if isOn == False:
        GPIO.output(fan,GPIO.LOW)
        return f'bi bi-slash-circle'
    else:
        GPIO.output(fan,GPIO.HIGH)
        return f'bi bi-fan'

#callback for temperature
@callback(
    [Output('temperature','value'),
     Output('fan-switch','on')],
    [Input('interval','n_intervals'),
     Input('fan-switch','on')]
)
def check_temperature(interval, isOn):
    # temp = DHT.get_temperature()
    temp = 25
    
    user = '2082991@iotvanier.com'
    password = '***REMOVED***'
    
    #have to check if fan is on
    if (temp > 24 and not isOn):
        if (not receive.check_email('The currenty temperature is', user, password)):
            message =  "The currenty temperature is {temp}. Would you like to turn on the fan?".format(temp=temp)
            send.send_email(message, user, password)
        else:
            print("a")
            if (receive.check_email('HELL YES', user, password)):
                #turn on fan
                print("a")
                return temp, True

    #have to check if fan is on
#     if (temp > 24):
#         if (receive.test()):
#             print("email send")
#             send.test()
#         else:
#             send.test()
#             print("reply yes send")
#             #turn on fan
#             
#             print("a")
#             return temp, True

    return temp, isOn

# # callback for temperature
# @callback(
#     Output('temperature','value'),
#     Input('interval','n_intervals')
# )
# def check_temperature(interval):
#     #return DHT.get_humidity()
#     return 22

# callback for humidity
@callback(
    Output('humidity','value'),
    Input('interval','n_intervals')
)
def check_humidity(interval):
    #return DHT.get_humidity()
    return 52
