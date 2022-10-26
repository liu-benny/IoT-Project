import dash
from dash import html, Output, Input, callback, dcc
import dash_daq as daq
import dash_bootstrap_components as dbc

# email scripts
from email_func import send, receive

#Libraries
#import components.DHT11.DHT11 as DHT
import RPi.GPIO as GPIO

from time import sleep
#Disable warnings (optional)
GPIO.setwarnings(False)
#Select GPIO mode
GPIO.setmode(GPIO.BCM)

#Set light - pin 23 as output
light=23
GPIO.setup(light,GPIO.OUT)                                                         

#Set fan pin
fan1=21
fan2=13
fan3=19
GPIO.setup(fan1,GPIO.OUT) 
GPIO.setup(fan2,GPIO.OUT) 
GPIO.setup(fan3,GPIO.OUT) 

#bool for fan and email sent
emailSent=False

box_style_dict = {
    'width': '45%',
    'border': '3px solid gray',
    'margin': '2.5%',
    'height': '450px'
}

box_name_dict = {
    'border-bottom': '2px solid lightblue',
    'line-height' : '50px',
    'font': 'bold 20px/50px Arial, sans-serif',
    'height': '50px'
}

layout = html.Div([
    html.Div([
        html.Div(['Lights',
        ], 
        style = box_name_dict
        ),
        
        html.Div([
            html.I(id='lightbulb',
            className="bi bi-lightbulb",
            style={'font-size': '10rem','width':'500px','padding-top': '60px'}),
            
            daq.BooleanSwitch(
                id='light-switch',
                on=True,
                color='#00EA64',
                style={'transform': 'scaleX(1.25) scaleY(1.25)'}
            ),
            
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
            )
        ], 
        
        style = {'float':'right', 'width': '33%','padding-top': '25px'}
        ),
    ], 
    
    style = box_style_dict| {'float': 'right'}
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
        GPIO.output(fan1,GPIO.LOW)
        GPIO.output(fan2,GPIO.LOW)
        GPIO.output(fan3,GPIO.LOW)
        return f'bi bi-slash-circle text-danger'
    else:
        GPIO.output(fan1,GPIO.HIGH)
        GPIO.output(fan2,GPIO.HIGH)
        GPIO.output(fan3,GPIO.LOW)
        return f'bi bi-fan text-success'

#callback for temperature
@callback(
    [Output('temperature','value'),
     Output('fan-switch','on')],
    [Input('interval','n_intervals'),
     Input('fan-switch','on')]
)
def check_temperature(interval, isOn):
    temp = DHT.get_temperature()
    
    user = '2082991@iotvanier.com'
    password = 'd34HqY87m6bL'
    
    #have to check if fan is on
    if (temp > 24 and not isOn):
        if (not receive.check_email('The current temperature is', user, password)):
            message =  "The current temperature is {temp}. Would you like to turn on the fan?".format(temp=temp)
            send.send_email(message, user, password)
        else:
            if (receive.check_email('YES', user, password)):
                #turn on fan
                message =  "Fan has turned on."
                send.send_email(message, user, password)
                
                return temp, True

    return temp, isOn

# callback for humidity
@callback(
    Output('humidity','value'),
    Input('interval','n_intervals')
)
def check_humidity(interval):
    return DHT.get_humidity()
