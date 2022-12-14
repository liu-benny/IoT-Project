import dash
from dash import html, Output, Input, callback
import dash_daq as daq
import dash_bootstrap_components as dbc

#Libraries
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
    )
    ],
    
    style={'text-align': 'center'}
    )
    
    

@callback(
    Output('lightbulb', 'class'),
    # Input('my-indicator-button-1', 'n_clicks'),
    Input('light-switch','on')
)

def update_output(isOn):
    if isOn == False:
        GPIO.output(buzzer,GPIO.LOW)
        return f'bi bi-lightbulb-off text-danger'
    else:
        GPIO.output(buzzer,GPIO.HIGH)
        return f'bi bi-lightbulb-fill text-success'

