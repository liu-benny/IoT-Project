import dash
from dash import html, Output, Input, callback, dcc
import dash_daq as daq
import dash_bootstrap_components as dbc

#Libraries
import components.DHT11.DHT11 as DHT
import RPi.GPIO as GPIO
from time import sleep
#Disable warnings (optional)
GPIO.setwarnings(False)
#Select GPIO mode
GPIO.setmode(GPIO.BCM)
#Set buzzer - pin 23 as output
buzzer=19
GPIO.setup(buzzer,GPIO.OUT)                                                         



layout = html.Div([

    html.I(id='lightbulb',
    className="bi bi-lightbulb",
    style={'font-size': '10rem','width':'500px',
    'padding': '50px'}),
    
    daq.BooleanSwitch(
        id='light-switch',
        on=True,
        color='#00EA64',
        style={'transform': 'scaleX(1.25) scaleY(1.25)'}
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
    )
    ])
    ],
    
    style={'text-align': 'center'}


)
    
    

@callback(
    Output('lightbulb', 'class'),
    # Input('my-indicator-button-1', 'n_clicks'),
    Input('light-switch','on')
)

def check_light_switch(isOn):
    if isOn == False:
        GPIO.output(buzzer,GPIO.LOW)
        return f'bi bi-lightbulb-off text-danger'
    else:
        GPIO.output(buzzer,GPIO.HIGH)
        return f'bi bi-lightbulb-fill text-success'

@callback(
    Output('temperature','value'),
    Input('interval','n_intervals')
)
def check_temperature(interval):
    return DHT.get_temperature()
