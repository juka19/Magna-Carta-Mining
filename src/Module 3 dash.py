import re
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components.Container import Container
from dash.dependencies import Input, Output
from pickle import load
import networkx as nx
import json
import plotly.io as pio
import plotly.graph_objects as go
import spacy

# load spacy model for classifier
nlp = spacy.load("output/model-best")

# load all plots from module 3
network_plot = pio.read_json('output/plotly_network.json')
line_plot = pio.read_json('output/plotly_bycountry.json')
cm_plot = pio.read_json('output/plotly_cm.json')
judges_plot = pio.read_json('output/plotly_sb_judge.json')
articles_plot = pio.read_json('output/plotly_sb_art.json')

# assign logo hrefs
echr_logo = 'https://www.mediadefence.org/wp-content/uploads/2020/06/Logo_European_Court_of_Human_Rights_1_linedrawing.jpg'
github_logo = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'

# links to github & hudoc
hudoc_link = 'https://hudoc.echr.coe.int/eng#{%22documentcollectionid2%22:[%22GRANDCHAMBER%22,%22CHAMBER%22]}'
github_link = 'https://github.com/juka19/Magna-Carta-Mining'

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUMEN],
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale= 1.0'}]) # importing bootstrap css theme Lumen


# Create top bar
navbar = dbc.Row(
    dbc.Container(
            dbc.Row(
                [
                    dbc.Col(html.A([html.Img(src=echr_logo, height='60px')], href=hudoc_link), width=1, className='float-left'),
                    dbc.Col(html.H2("Magna Carta Mining"), width={'size': 6, 'offset':2}, className='ms-2 text-center'),
                    dbc.Col(html.A([html.Img(src=github_logo, height='60px')], href=github_link), className='float-right', width={'size': 1, 'offset':2})
                ],
                align='center', className='g-0'
            )
    )
)

# Create layout: Very simple, header & 5 tabs
app.layout = html.Div([
    navbar, 
    dbc.Row(
        dbc.Col(
            html.Div(
                children=[
                    dcc.Tabs(id="tabs", value="tab-1", children=[
                        dcc.Tab(label="Overview", value='tab-1'),
                        dcc.Tab(label="Judgments over Time", value='tab-2'),
                        dcc.Tab(label="Network Graph", value='tab-3'),
                        dcc.Tab(label="Text Classification", value='tab-4'),
                        dcc.Tab(label='Allegations by Country, Article & Judge', value='tab-5')
                    ], className='mb-4 h4 text-center'),
                    html.Div(id='tab-content')
                ], style={'margin':'auto', 'padding': '30px', 'align': 'center', 'font-family': 'Sans-serif'})
        )
    )
])

# Create callback for tabs
@app.callback(Output('tab-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Overview'),
            html.Div(children=[
                html.H1("Magna Carta Mining"),
                html.P("""Every person that is located in the European Union’s territory has and is owed human rights, which they can assert against the State, companies, the police, and your fellow Hertie lecturers or class mates. However, people are unaware of what their rights are, how rights evolve, and what rights even mean. The HUDOC European Union Court of Human Rights database provides access to all the relevant European Union human rights case law. However, this database fails at making this law accessible to the people it serves."""),
                html.P("""Magna Carta Mining fills the gap left by HUDOC and makes the legal information accessible to the European Union’s population by providing the relevant information in a manner that is readily understandable (data visualisation), providing the user with the the ability to identify trends in human rights issues, and with the ability to download documents en masse. The data visualisations pertain to rights based issues that are generalised or specific to the user."""),
                html.P("""Specific information can be selected by the user who will be provided with a multitude of infographics which they can manipulate. Examples of human rights information that the user can identify include, but is not limited to: the change in human rights issues over time; the number of cases decided by European Member States in any given year; or the most topical issue for any or all European Member States.""")
            ], style={'height': '50%', 'width':'80%', 
            'background-color':'rgb(83, 130, 241)', 
            'margin': 'auto', 'font-family': 
            'Sans-serif', 'padding': '20px', 
            'color': 'white'}, className='rounded')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Judgments over Time'),
            dcc.Graph(
                id='line_plot',
                figure=line_plot,
                style={'width': '100%', 'height': '60%', 'margin': 'auto'}
            )
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Network Graph'),
            dcc.Graph(
               id='network_plot',
               figure=network_plot,
               style={'width': '70%', 'height': '800px', 'margin': 'auto'} 
            )
        ])
    elif tab == 'tab-4':
        return html.Div([
            html.H3('Text Classification'),
            html.P('Does your text violate human rights? Input text to find out!'),
            dcc.Textarea(
                id='text-input',
                value="""
                ALLEGED VIOLATION OF ARTICLE 10 OF THE CONVENTION ON ACCOUNT OF THE APPLICANT’S CRIMINAL CONVICTION
                77.  The applicant complained under Article 10 of the Convention about his criminal conviction on account of his editorial choices relating to the publication of the material under the headline “Death to Russia!”.
                78.  The relevant parts of Article 10 of the Convention read as follows:
                “1.  Everyone has the right to freedom of expression. This right shall include freedom to hold opinions and to receive and impart information and ideas without interference by public authority and regardless of frontiers. ...
                2.  The exercise of these freedoms, since it carries with it duties and responsibilities, may be subject to such formalities, conditions, restrictions or penalties as are prescribed by law and are necessary in a democratic society, in the interests of national security, territorial integrity or public safety, for the prevention of disorder or crime, for the protection of health or morals, for the protection of the reputation or rights of others, for preventing the disclosure of information received in confidence, or for maintaining the authority and impartiality of the judiciary.”""",
                style={'width': '100%', 'height': 300},
            ),
            html.Br(),
            html.H5('Model Prediction'),
            html.Div(id='model-output', style={'whiteSpace': 'pre-line'}),
            html.Br(),
            html.H3('Confusion Matrix of Text Classifier'),
            dcc.Graph(
               id='cm_plot',
               figure=cm_plot,
               style={'width': '100%', 'height': '100%'}
            )
        ])
    elif tab == 'tab-5':
        return html.Div([
            html.H3('Sunburst Plots of Allegations by Country'),
            dcc.Graph(
               id='articles_plot',
               figure=articles_plot,
               style={'width': '700px', 'height': '700px', 'margin': 'auto', 'display': 'inline-block'} 
            ),
            dcc.Graph(
               id='judges_plot',
               figure=judges_plot,
               style={'width': '700px', 'height': '700px', 'margin': 'auto', 'display': 'inline-block'} 
            )
        ])
# Create callback for Text classifier
@app.callback(Output('model-output', 'children'), Input('text-input', 'value'))
def update_output(value):
    return f"Probability of no violation: {round(nlp(value).cats['no_violation'], 2)} | Probability of violation: {round(nlp(value).cats['violation'], 2)} | Probability of Other: {round(nlp(value).cats['other'], 2)} | Probability of Mixed: {round(nlp(value).cats['mixed'], 2)}"

if __name__ == '__main__':
    app.run_server(debug=True)