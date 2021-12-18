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
    ], style={'margin':'auto', 'padding': '30px', 'align': 'center'})

@app.callback(Output('tab-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Overview'),
            html.Div(children=[
                html.H1("Project Title"),
                html.H5("""Every person that is located in the European Union’s territory has and is owed human rights, which they can assert against the State, companies, the police, and your fellow Hertie lecturers or class mates. However, people are unaware of what their rights are, how rights evolve, and what rights even mean. The HUDOC European Union Court of Human Rights database provides access to all the relevant European Union human rights case law. However, this database fails at making this law accessible to the people it serves."""),
                html.H5("""Magna Carta Mining fills the gap left by HUDOC and makes the legal information accessible to the European Union’s population by providing the relevant information in a manner that is readily understandable (data visualisation), providing the user with the the ability to identify trends in human rights issues, and with the ability to download documents en masse. The data visualisations pertain to rights based issues that are generalised or specific to the user."""),
                html.H5("""Specific information can be selected by the user who will be provided with a multitude of infographics which they can manipulate. Examples of human rights information that the user can identify include, but is not limited to: the change in human rights issues over time; the number of cases decided by European Member States in any given year; or the most topical issue for any or all European Member States.""")
            ], style={'height':400, 'width':800, 'background-color':'cornflowerblue', 'margin': 'auto', 'font-family': 'Sans-serif', 'padding': '10px', 'color': 'white'})
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Judgments over Time'),
            dcc.Graph(
                id='line_plot',
                figure=line_plot,
                style={'width': '100vh', 'height': '90vh', 'margin': 'auto'}
            )
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Network Graph'),
            dcc.Graph(
               id='network_plot',
               figure=network_plot,
               style={'width': '100vh', 'height': '90vh', 'margin': 'auto'} 
            )
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Text Classification'),
            dcc.Graph(
               id='cm_plot',
               figure=cm_plot,
               style={'width': '100vh', 'height': '90vh', 'margin': 'auto'}
            )
        ])

if __name__ == '__main__':
    app.run_server(debug=True)