# Import necessary libraries 
from dash import html, dcc, Input, Output
from dash.dependencies import Input, Output
import dash
import dash_bootstrap_components as dbc

import plotly.express as px
from dash_bootstrap_templates import ThemeSwitchAIO

# Connect to main app.py file
from app import app

# Connect to your app pages
# from pages import page1, page2
from pages import page1

# Connect the navbar to the index
from components import navbar

# define the navbar
nav = navbar.Navbar()

# define bootstrap icons
app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP, dbc.themes.COSMO]
)

# Define the index page layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    nav, 
    html.Div(id='page-content', children=[]), 
])

@app.callback(
     Output("theme-switch-graph", "figure"),
     Input(ThemeSwitchAIO.ids.switch("theme"), "value"),
)
def update_graph_theme(toggle):
    template = "cosmo" if toggle else "DARKLY"
    return px.line(template=template)


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    return page1.layout

# Run the app on localhost:8050
if __name__ == '__main__':
    app.run_server(debug=False)
