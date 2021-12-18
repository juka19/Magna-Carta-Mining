from math import nan
from collections import Counter
import re
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from pickle import load
import networkx as nx
import json
import plotly.io as pio
import plotly.graph_objects as go



network_plot = pio.read_json('output/plotly_network.json')
line_plot = pio.read_json('output/plotly_bycountry.json')
cm_plot = pio.read_json('output/plotly_cm.json')

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.Img(src='https://www.europewatchdog.info/wp-content/uploads/2014/01/COE-logo-ECHR.png'),
        html.H1("Magna Carta Mining Dashboard"),
        dcc.Tabs(id="tabs", value="tab-1", children=[
            dcc.Tab(label="Overview", value='tab-1'),
            dcc.Tab(label="Judgments over Time", value='tab-2'),
            dcc.Tab(label="Network Graph", value='tab-3'),
            dcc.Tab(label="Text Classification", value='tab-4'),
        ]),
        html.Div(id='tab-content')
    ])

@app.callback(Output('tab-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Overview'),
            html.Div(children=[
                html.H1("Project Title"),
                html.H2("Description, blabla")
            ], style={'height':250, 'width':250, 'background-color':'cornflowerblue'})
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Judgments over Time'),
            dcc.Graph(
                id='line_plot',
                figure=line_plot,
                style={'width': '100vh', 'height': '90vh'}
            )
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Network Graph'),
            dcc.Graph(
               id='network_plot',
               figure=network_plot,
               style={'width': '100vh', 'height': '90vh'} 
            )
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Text Classification'),
            dcc.Graph(
               id='cm_plot',
               figure=cm_plot,
               style={'width': '100vh', 'height': '90vh'}
            )
        ])

if __name__ == '__main__':
    app.run_server(debug=True)