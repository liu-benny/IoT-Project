# Import necessary libraries
from dash import html
import dash_bootstrap_components as dbc

# import plotly.express as px
# from dash_bootstrap_templates import ThemeSwitchAIO

# theme_switch = ThemeSwitchAIO(aio_id="theme", themes=[dbc.themes.COSMO, dbc.themes.CYBORG])
# Define the navbar structure
def Navbar():

    layout = dbc.NavbarSimple(
    children=[
        # dbc.NavItem(dbc.NavLink("Page 1", href="/page1")),
        # dbc.NavItem(dbc.NavLink("Page 2", href="/page2")),
        dbc.DropdownMenu(
            children=[
#                 dbc.DropdownMenuItem("Theme", header=True),#############################################################################################
#                 dbc.Container([theme_switch], className="m-4 dbc"),#############################################################################################
            ],
            nav=True,
            in_navbar=True,
#             label="Theme Color",#############################################################################################
        ),
    ],
    style={
        'min-width' : '1500px'
    },
    brand="Smart Home",
    
    brand_href="/page1",
    color="rgb(96, 107, 124)",
    dark=True)
    #])


    return layout
