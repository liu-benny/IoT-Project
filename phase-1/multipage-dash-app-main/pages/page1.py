import dash
import dash_daq as daq
from dash import html, Output, Input, callback, State
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
    # daq.Indicator(
    #     id='my-indicator-1',
    #     label="Default",
    #     width = 50,
    # ),
    daq.BooleanSwitch(
        id='light-switch',
        on=True,
        color='#00EA64',
    style={'transform': 'scaleX(1.25) scaleY(1.25)'}
    )
    ],
    
    style={'text-align': 'center'}
    )
    
    # daq.ToggleSwitch(
    #     id='darktheme-daq-toggleswitch',
    #     className='dark-theme-control'
    # ),

#     html.Button(
#         'On/Off',
#         id='my-indicator-button-1',
#         n_clicks=1,
#     style={'background-color': 'blue',
#            'border': '0',
#            'border-radius': '56px',
#   'color': 'green',
#            'cursor': 'pointer',
#            'font-size': '18px',
#   'font-weight': '600',
#   'outline': '0',
#   'padding': '16px 21px',
#   'position': 'relative',
#   'text-align': 'center',
#   'text-decoration': 'none',
#   'transition': 'all .3s',
#   'user-select': 'none',
#   '-webkit-user-select': 'none',
#   'touch-action': 'manipulation'
  
  
  
           
  
#   }
#     )
# ])

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
# def update_output(value):
#     if value % 2 !=  0:
#          GPIO.output(buzzer,GPIO.LOW)
#     if value % 2 == 0:
#         GPIO.output(buzzer,GPIO.HIGH)
#         return f'The swith value {value}.'

