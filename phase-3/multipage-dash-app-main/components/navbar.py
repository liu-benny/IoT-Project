# Import necessary libraries
from dash import html
import dash_bootstrap_components as dbc


# Define the navbar structure
def Navbar():

    layout = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Page 1", href="/page1")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Page 2", href="/page2"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    style={
        'min-width' : '800px'
    },
    brand="Smarth Home",
    brand_href="/page1",
    color="primary",
    dark=True)
    #])

    return layout
