# Import necessary libraries 
import dash
from dash import html, Output, Input, State, callback, dcc, ctx
import dash_daq as daq
import dash_bootstrap_components as dbc
import paho.mqtt.client as mqtt
import soundFunction
from datetime import datetime


# db class
from db.db_class import DbConnector

### Add the page components here 
admin_card = "aaaaaaaaaaa"
db_connection = DbConnector(admin_card)



class RfidScan:
    def __init__(self):
        self.id = None

rfid_id = RfidScan()

# Define the final page layout
layout = dbc.Container([
    html.Div([
        dcc.Input(
            id='user-id-input',
            disabled=True,
            size=50,
            placeholder='Scan your RFID tag',
            type='text',
            value=''
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("User Creation")),
                dbc.ModalBody("", id='alert_body'),
            ],
            id="alert",
            is_open=False,
        )
    ], className="mb-4"),
    
    html.Div([
        # name
        dcc.Input(
            id='name-input',
            size=50,
            placeholder='Enter your name',
            type='text'
        ),
    ], className="mb-4"),
    
    html.Div([
        # temp threshold
        daq.NumericInput(
            id='temp-threshold-input',
            disabled=False,
            size=150,
            min=-40,
            max=40,
        )
    ], className="mb-4"),
    
    html.Div([
        # humidity threshold
        daq.NumericInput(
            id='humidity-threshold-input',
            disabled=False,
            size=150,
            min=0,
            max=100,

        ),
    ], className="mb-4"),
    
    html.Div([
        # light intensity threshold
        daq.NumericInput(
            id='light-threshold-input',
            disabled=False,
            size=150,
            min=0,
            max=1000,

        ),
    ], className="mb-5"),
    
    html.Div([
        html.Button(
            'Submit', 
            disabled=True,
            id='submit-user-button'
        ),
    ], className="mb-4"),
      
    dcc.Interval(
        id='interval-component',
        interval=1000, # in milliseconds
        n_intervals=0
    )
], className="text-center mt-5"
                       )

# to disable/enable button
@callback(
    Output('submit-user-button', 'disabled'),
    [Input('user-id-input', 'value'),
     Input('name-input', 'value'),
     Input('temp-threshold-input', 'value'),
     Input('humidity-threshold-input', 'value'),
     Input('light-threshold-input', 'value')])
def enable_button(user_id, name, temp, humidity, light):
    if (user_id is not None and name is not None and temp is not None and humidity is not None and light is not None):
        return False
    return True

# to submit changes by clicking button
@callback(
    [Output('alert', 'is_open'),
     Output('alert_body', 'children')],
    [Input('submit-user-button', 'n_clicks')],
    [State('user-id-input', 'value'),
     State('name-input', 'value'),
     State('temp-threshold-input', 'value'),
     State('humidity-threshold-input', 'value'),
     State('light-threshold-input', 'value')])
def button_click(n_clicks, user_id, name, temp, humidity, light):
    
    if ("submit-user-button" == ctx.triggered_id):
        if (db_connection.insertUser(user_id, name, str(temp), str(humidity), str(light))):
            return True, "User has been created", None, None, None, None, None 
        else:
            return True, "User already exists", None, name, str(temp), str(humidity), str(light)
    
    return False, "", user_id, name, str(temp), str(humidity), str(light)

@callback(Output('user-id-input', 'value'),
          [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    return rfid_id.id


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("Smarthome/ESP/rfid")



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    
    if ('rfid' in msg.topic):
        rfid_id.id = str(msg.payload)[2:-1]




client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# client.connect("192.168.0.153", 1883, 80)
# client.loop_start()