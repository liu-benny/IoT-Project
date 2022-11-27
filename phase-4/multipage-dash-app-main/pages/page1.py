import dash
from dash import html, Output, Input, State, callback, dcc, ctx
import dash_daq as daq
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

# import for mqtt, light and rfid
import paho.mqtt.client as mqtt

# sound function for light and fan
import soundFunction

# email class and date for emails
from email_classes.email_logic import EmailController
from datetime import datetime

# db class
from db.db_class import DbConnector

# fake rpi ------------------------------------------------------------------TO REMOVE -
import sys
import fake_rpi

sys.modules['RPi'] = fake_rpi.RPi     # Fake RPi
sys.modules['RPi.GPIO'] = fake_rpi.RPi.GPIO # Fake GPIO
sys.modules['smbus'] = fake_rpi.smbus # Fake smbus (I2C)
# --------------------------------------------------------------------------------------


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
login_email_controller = EmailController('192.168.0.11', '2082991@iotvanier.com', 'd34HqY87m6bL', "Smart Home Login")

#Database connection with default admin card
admin_card = "aaaaaaaaaaa"
db_connection = DbConnector(admin_card)

#light level set outside of range of light sensor to start
class LightLevel:    
    def __init__(self, l):
        self.light_level = l

#rfid for user creation set to null to start
class RfidScan:
    def __init__(self, id):
        self.id = id
        # self.scan_new_card = False
        
lvl = LightLevel(-1)
rfid_id = RfidScan(admin_card)

# style for dashboard boxes
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

# style for box names
box_name_dict = {
    'border-bottom': '2px solid lightblue',
    'line-height' : '50px',
    'font': 'bold 20px/50px Arial, sans-serif',
    'height': '50px',
}

# style for information at the bottom of the boxes
box_bottom_dict = {
    'border-top': '2px solid lightblue',
    'line-height' : '40px',
    'font': 'bold 16px/40px Arial, sans-serif',
    'height': '40px',
    'width' : '50%',
    'padding' : '0px 10px',
    'position': 'absolute',
    'bottom': '0',
}

# style for the label at the bottom
box_label_dict = box_bottom_dict | {
    'background-color' : 'rgba(128, 128, 128, 0.2)',
    'text-align' : 'left',
    'left' : '0',
}

# style for the value at the bottom
box_num_dict = box_bottom_dict | {
    'background-color' : 'rgba(192, 192, 192, 0.2)',
    'text-align' : 'right',
    'right' : '0',
}

# page layout
layout = html.Div([
    # modal for light information
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Light")),
            dbc.ModalBody("Email sent."),
        ],
        id="light-modal",
        is_open=False,
    ),

    # modal for user update
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("User Update")),
            dbc.ModalBody("", id='user-update-modal-body'),
        ],
        id="user-update-modal",
        is_open=False,
    ), 

    # modal for user login
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("User Login")),
            dbc.ModalBody("", id='user-login-modal-body'),
        ],
        id="user-login-modal",
        is_open=False,
    ), 

    # interval for refreshing values
    dcc.Interval(id='interval',interval=5*1000, n_intervals=0),

    # user info column
    html.Div([
        html.Div([
            html.H2(["User Profile"]),

            html.Div([
                html.Div([
                    dcc.Input(
                        id='user-id-input',
                        disabled=True,
                        placeholder='Scan your RFID tag',
                        type='text',
                        value='',
                        style= {"width" : "100%"}
                    )], 
                    className="mb-3",
                    style= {"width" : "100%"}
                ),
                
                html.Div([
                    # name
                    dcc.Input(
                        id='name-input',
                        placeholder='Enter your name',
                        type='text',
                        style= {"width" : "100%"}
                    )], 
                    className="mb-3",
                    style= {"width" : "100%"}
                ),
                
                html.Div([
                    # temp threshold
                    daq.NumericInput(
                        id='temp-threshold-input',
                        disabled=False,
                        size=200,
                        min=-40,
                        max=40,
                        style= {"width" : "100%"},
                    )], 
                    className="mb-3",
                    style= {"width" : "100%"}
                ),
                
                html.Div([
                    # humidity threshold
                    daq.NumericInput(
                        id='humidity-threshold-input',
                        disabled=False,
                        size=200,
                        min=0,
                        max=100,
                        style= {"width" : "100%"}
                    )], 
                    className="mb-3",
                    style= {"width" : "100%"}
                ),
                
                html.Div([
                    # light intensity threshold
                    daq.NumericInput(
                        id='light-threshold-input',
                        disabled=False,
                        min=0,
                        max=1000,
                        style= {"width" : "100%"}
                    )], 
                    className="mb-3",
                    style= {"width" : "100%"}
                ),
                
                html.Div([
                    dbc.Button(
                        'Submit Changes', 
                        disabled=True,
                        id='submit-user-button',
                        style= {"width" : "100%"}
                    )], 
                    className="mb-3",
                    style= {"width" : "100%"}
                )],
                
                className="input-group mt-5"
            ),
        ],
        style = {
            'text-align': 'left',
            'padding': '25px',
            'height': '900px',
            'min-width' : "250px", 
            'width' : "100%", 
            'display': 'inline-block',
            'background-color' : 'rgba(177, 177, 177, 0.4)'
        }),
    ],
        style = {
            'text-align': 'center',
            'padding': '25px',
            'height': '100%',
            'width' : '20%',
            'min-width' : "300px", 
            'float': 'left',
            'background-color' : 'rgb(236, 237, 238)'
        }
    ),

    # page content
    html.Div([
        html.H1(["Smart Home Dashboard"]),
        # first box for lights
        html.Div([
            html.Div(
                ['Lights Control'], 
                style = box_name_dict | {'background-color' : 'rgba(239, 190, 125, 0.55)'}
            ),
            
            html.Div([
                # lightbulb icon
                html.I(
                    id='lightbulb',
                    className="bi bi-lightbulb-off text-danger",
                    style={'font-size': '10rem','width':'500px','padding-top': '60px'}
                ),
                
                # light control switch
                daq.BooleanSwitch(
                    id='light-switch',
                    on=False,
                    color='#00EA64'
                )],

                style = {'float': 'left', 'width' : '100%', 'padding-top' : '25px'}
            ),
            
            # light intensity value
            html.Div([
                html.Div(['Light intensity'], style = box_label_dict),
                html.Div(['Checking...'], id='light-number', style = box_num_dict)
            ]),
            html.Div([
                html.Div(['Light status'], style = box_label_dict | {"bottom" : "40px"}),
                html.Div(['Off'], id='light-status', style = box_num_dict | {"bottom" : "40px"})]
            )], 
            
            style = box_style_dict | {'float': 'left'}
        ),
        
        # box for fan
        html.Div([
            html.Div(
                ['Fan Control',], 
                style = box_name_dict | {'background-color' : 'rgba(139, 211, 230, 0.55)'}
            ),
            
            html.Div([
                # fan icon
                html.I(
                    id='fan',
                    className="bi bi-slash-circle text-danger",
                    style={'font-size': '10rem','width':'30px'}
                ),
                
                #fan control switch
                daq.BooleanSwitch(
                    id='fan-switch',
                    on=False,
                    color='#00EA64'
                )], 
                
                style = {'float':'left', 'width' : '100%', 'padding-top': '25px'}
            ),
            
            html.Div([
                html.Div(['Fan status'], style = box_label_dict),
                html.Div(['Off'], id='fan-status', style = box_num_dict)
            ])], 
        
            style = box_style_dict| {'float': 'left'}
        ),
        
        # box for temperature detection
        html.Div([
            html.Div(
                ['Temperature Detection'], 
                style = box_name_dict | {'background-color' : 'rgba(177, 162, 202, 0.55)'}
            ),
            
            html.Div([
                # temperature indicator (gauge)
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
            
            # temperature value
            html.Div([
                html.Div(['Temperature'], style = box_label_dict),
                html.Div(['Checking...'], id='temp-number', style = box_num_dict)
            ])], 
        
            style = box_style_dict | {'float': 'left'}
        ),
        
        # box for humidity detection
        html.Div([
            html.Div(
                ['Humidity Detection',], 
                style = box_name_dict | {'background-color' : 'rgba(255, 109, 106, 0.55)'}
            ),
            
            # humidity indicator (thermometer icon)
            html.Div([
                daq.Thermometer(
                    id='humidity',
                    color="orange",
                    value=0,
                    scale={'start':0,'interval':5},
                    max=100,
                    min=-0,
                    style={'transform': 'scaleX(0.80) scaleY(0.80)'}
                )], 
            
                style = {'float':'right', 'width' : '100%', 'padding-top': '25px'}
            ),
            
            html.Div([
                html.Div(['Humidity'], style = box_label_dict),
                html.Div(['Checking...'], id='humidity-number', style = box_num_dict),
            ])], 
        
            style = box_style_dict | {'float': 'left'}
        ),
        
        # to clear all the boxes for background to reach bottom
        html.Div(
            [], 
            className = 'spacer',
            style = {'clear': 'both'}
        )],
        
        style={
            'text-align': 'center',
            'padding': '25px',
            'height' : '100%',
            'width' : '80%',
            'float': 'right',
            'min-width' : '1200px'
        }
    )],

    style= {            
        'min-width' : '1500px',
        'height' : '100%'
    }
)


# callback for LED light-number
@callback(
    [Output('lightbulb', 'className'),
     Output('light-switch','on'),
     Output('light-modal','is_open'),
     Output('light-status', 'children')],
    [Input('light-switch','on'),
     Input('interval','n_intervals')],
    [State('lightbulb', 'className'),
     State('light-modal','is_open')]
)
def check_light_switch(isOn, interval, light_indicator, modal_open):
    if isOn == False:
        # if fan is off and light level is less than threshold with no email sent
        if (lvl.light_level > 0 and lvl.light_level < db_connection.current_light_threshold and not light_email_controller.sent):
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%Y-%m-%d")
            
            # light_email_controller.send_email('Light is lower than 200. Turning on lights at ' + current_time + ' on ' + current_date)
            light_email_controller.sent = True
            print("email sent")
            
            GPIO.output(light,GPIO.HIGH)
            soundFunction.lightOn()

            return f'bi bi-lightbulb-fill text-success', True, True, "On"
        
        # if email is already sent or if light level is high, do not change
        else:
            GPIO.output(light,GPIO.LOW)
            # light_email_controller.sent = False
            
            if not 'danger' in light_indicator:
                soundFunction.lightOff()
            
            return f'bi bi-lightbulb-off text-danger', False, modal_open, "Off"
    
    # once over threshold, allows email to be sent again later. otherwise, remove if here and add in else above.
    if (lvl.light_level > 0 and lvl.light_level > db_connection.current_light_threshold):
        light_email_controller.sent = False

    # turn light on
    if not 'success' in light_indicator:
        soundFunction.lightOn()

    GPIO.output(light,GPIO.HIGH)
    return f'bi bi-lightbulb-fill text-success', True, modal_open, "On"


# callback for updating light level
@callback(
    Output('light-number','children'),
    Input('interval','n_intervals')
)
def update_intensity(interval):
    # if light level has not been checked yet
    if (lvl.light_level < 0):
        return "Checking..."
    else:
        return str(lvl.light_level)


# callback for motor/fan
@callback(
    [Output('fan','className'),
     Output('fan-status', 'children')],
    Input('fan-switch','on'),
    State('fan', 'className')
)
def check_fan_switch(isOn, fan_indicator):
    print(fan_indicator)

    # checks if the state of fan and switch is matching to skip
    if isOn == False:
        GPIO.output(fan1,GPIO.LOW)
        GPIO.output(fan2,GPIO.LOW)
        GPIO.output(fan3,GPIO.LOW)

        if not 'danger' in fan_indicator:
            soundFunction.fan2()

        return f'bi bi-slash-circle text-danger', "Off"
    else:
        GPIO.output(fan1,GPIO.HIGH)
        GPIO.output(fan2,GPIO.HIGH)
        GPIO.output(fan3,GPIO.LOW)
        
        # allows email to be received again, once manually turning on then turning off in the future
        fan_email_controller.received = False
        
        if not 'success' in fan_indicator:
            soundFunction.fan()

        return f'bi bi-fan text-success', "On"


#callback for temperature
@callback(
    [Output('temp-number', 'children'),
     Output('temperature','value'),
     Output('fan-switch','on')],
    [Input('interval','n_intervals'),
     Input('fan-switch','on')]
)
def check_temperature(interval, isOn):
    # temp = DHT.get_temperature()
    temp = 22
    
    # check if fan is on, temp is over threshold.
    # received has to be checked since it needs response
    if (temp > db_connection.current_temp_threshold and isOn == False and not fan_email_controller.received):
        if (not fan_email_controller.sent):
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            current_date = now.strftime("%Y-%m-%d")
            message =  "The current temperature is {temp} at {time} on {date}. Would you like to turn on the fan?".format(temp=temp, time=current_time, date=current_date)
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
    [Output('humidity-number', 'children'),
     Output('humidity','value')],
    [Input('interval','n_intervals')]
)
def check_humidity(interval):
    # return DHT.get_humidity() + "%", DHT.get_humidity()
    return str(22) + "%", 22


# to disable/enable button for changing thesholds
@callback(
    Output('submit-user-button', 'disabled'),
    [Input('name-input', 'value'),
     Input('temp-threshold-input', 'value'),
     Input('humidity-threshold-input', 'value'),
     Input('light-threshold-input', 'value'),
     Input('submit-user-button', 'n_clicks')])
def enable_button(name, temp, humidity, light, n_clicks):
    if ("submit-user-button" == ctx.triggered_id):
        return True
    
    if (
        name != db_connection.current_name or
        temp != db_connection.current_temp_threshold or
        humidity != db_connection.current_humidity_threshold or
        light != db_connection.current_light_threshold
    ):
        
        return False
    
    return True


# callback to submit changes by clicking button
@callback(
    [Output('user-update-modal', 'is_open'),
     Output('user-update-modal-body', 'children')],
    [Input('submit-user-button', 'n_clicks')],
    [State('user-id-input', 'value'),
     State('name-input', 'value'),
     State('temp-threshold-input', 'value'),
     State('humidity-threshold-input', 'value'),
     State('light-threshold-input', 'value')]
)
def button_click(n_clicks, user_id, name, temp, humidity, light):
    if ("submit-user-button" == ctx.triggered_id):
        if (db_connection.updateThresholds(user_id, name, str(temp), str(humidity), str(light))):
            db_connection.updateCurrentUser(user_id)
            return True, "User has been updated"
        else:
            return True, "User could not be updated"
    
    raise PreventUpdate()

# callback to update rfid when scanned for user login
@callback(
    [Output('user-id-input', 'value'),
     Output('user-login-modal', 'is_open'),
     Output('user-login-modal-body', 'children')],
    [Input('interval', 'n_intervals')],
    [State('user-id-input', 'value')]
)
def update_user_id(interval, user_id):
    if (user_id == rfid_id.id):
        raise PreventUpdate()
    
    if db_connection.updateCurrentUser(rfid_id.id):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")
        # login_email_controller.send_email("User " + user_id + " has logged in at " + current_time + "on"  + current_date)
        
        return db_connection.current_user_id, True, "User " + user_id + " logged in successfully."
    
    return user_id, True, "User " + rfid_id.id + " not found, could not log in."


# callback to change values when user logs in
@callback(
    [Output('name-input', 'value'),
     Output('temp-threshold-input', 'value'),
     Output('humidity-threshold-input', 'value'),
     Output('light-threshold-input', 'value')],
    [Input('user-id-input', 'value')]
)
def update_user_profile(user_id):
    return db_connection.current_name, db_connection.current_temp_threshold, db_connection.current_humidity_threshold, db_connection.current_light_threshold


# callback for receiving CONNACK response from mqtt server
def on_connect(client, userdata, flags, rc):
    # subscribing to topics
    client.subscribe("Smarthome/ESP/light")
    client.subscribe("Smarthome/ESP/rfid")

# callback for published message from mqtt server
def on_message(client, userdata, msg):
    # changing light
    if ('light' in msg.topic):
        lvl.light_level = float(str(msg.payload)[2:-1])

    # changing rfid login
    if ('rfid' in msg.topic):
        rfid_id.id = str(msg.payload)[2:-1]
        # db_connection.updateCurrentUser(str(msg.payload)[2:-1])

# setting up mqtt
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# connecting mqtt
# client.connect("192.168.0.153", 1883, 80)
# client.loop_start()