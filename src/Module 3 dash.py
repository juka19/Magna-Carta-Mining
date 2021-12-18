from math import nan
from collections import Counter
import re
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from pickle import load
import networkx as nx
import plotly.express as px

with open('data_cleaned.pickle', 'rb') as handle:
    df = load(handle)

df['year'] = df['date'].dt.year
by_country_over_time = df.groupby(['year', 'respondent_state']).size()

fig1 = px.line(
    by_country_over_time, 
    x=by_country_over_time.index.get_level_values(0), 
    y=by_country_over_time.values, 
    color=by_country_over_time.index.get_level_values(1), 
    line_group=by_country_over_time.index.get_level_values(1),
    markers=True
)
fig1.update_layout(
    title="ECHR Judgements by Country over Time",
    xaxis_title="Year",
    yaxis_title="Number of Judgements",
    font=dict(
        family="Roboto",
        size=18,
        color="#7f7f7f"
    ) 
)
fig1.update_traces(
    hovertemplate="<br>".join([
        "Year: %{x}",
        "Cases: %{y}"
    ])
)

fig1.show()

# network graph:

nodes = [(re.findall('\d{3,5}\/\d{2}', row)[0], l, c) for row, l, c in zip(df['ident'], df['related_cases'], df['respondent_state']) if re.findall('\d{3,5}\/\d{2}', row)]

G = nx.Graph()
for node in nodes:
    if node[0] not in G:
        G.add_node(node[0], weight=0.1, role=node[2], size = 1)
        if node[1]:
            for i in node[1]:
                if G.has_edge(node[0], i):
                    G[node[0]][i]['weight'] += 1
                else:
                    G.add_edge(node[0], i, weight=1)
    
G.remove_nodes_from(list(nx.isolates(G)))

pos=nx.spring_layout(G, scale=2)
plt.figure(3,figsize=(12,12))
nx.draw(G, pos, node_size=60)

plt.show()

# look for Cytoscope    


for node in list(G.nodes):
    if len(G.edges(node)) < 5:
        G.remove_node(node) """

pos_ = nx.spring_layout(G)

""" def make_edge(x, y, text, width):
    return  go.Scatter(x         = x,
                       y         = y,
                       line      = dict(width = width,
                                   color = 'cornflowerblue'),
                       hoverinfo = 'text',
                       text      = ([text]),
                       mode      = 'lines')

edge_trace = []
for edge in G.edges():
    if G.edges()[edge]['weight'] > 0:
        char_1 = edge[0]
        char_2 = edge[1]
        x0, y0 = pos_[char_1]
        x1, y1 = pos_[char_2]
        text = char_1 + '--' + char_2 + ': ' + str(G.edges()[edge]['weight'])
        trace  = make_edge([x0, x1, None], [y0, y1, None], text, width = 0.3*G.edges()[edge]['weight']**1.75)
        edge_trace.append(trace)

node_trace = go.Scatter(x         = [],
                        y         = [],
                        text      = [],
                        textposition = "top center",
                        textfont_size = 10,
                        mode      = 'markers+text',
                        hoverinfo = 'none',
                        marker    = dict(color = [],
                                         size  = [],
                                         line  = None))

for node in G.nodes():
    x, y = pos_[node]
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])
    node_trace['marker']['color'] += tuple(['cornflowerblue'])
    node_trace['text'] += tuple(['<b>' + node + '</b>'])


    layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)', # transparent background
    plot_bgcolor='rgba(0,0,0,0)', # transparent 2nd background
    xaxis =  {'showgrid': False, 'zeroline': False}, # no gridlines
    yaxis = {'showgrid': False, 'zeroline': False}, # no gridlines
)
# Create figure
fig = go.Figure(layout = layout)
# Add all edge traces
for trace in edge_trace:
    fig.add_trace(trace)
# Add node trace
fig.add_trace(node_trace)
# Remove legend
fig.update_layout(showlegend = False)
# Remove tick labels
fig.update_xaxes(showticklabels = False)
fig.update_yaxes(showticklabels = False)
# Show figure
fig.show()




elements_1 = [{'data': {'id': node, 'label': node}} if len(G.edges(node)) > 6 else G.remove_node(node) for node in list(G.nodes)]
elements_2 = [{'data': {'source': edge[0], 'target': edge[1], 'weight': G.get_edge_data(edge[0], edge[1])['weight']}} for edge in G.edges]


app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown-nw-layout',
        value='grid',
        clearable=False,
        options=[
            {'label': name.capitalize(), 'value': name}
            for name in ['grid', 'random', 'circle', 'cose', 'concentric']
        ]
    ),
    cyto.Cytoscape(
        id='network',
        layout={'name': 'grid'},
        style={'width': '100%', 'height': '450px'},
        elements=elements_1+elements_2
    )
])

@app.callback(Output('network', 'layout'), Input('dropdown-nw-layout', 'value'))
def update_layout(layout):
    return {
        'name': layout,
        'animate': True
    }

if __name__ == '__main__':
    app.run_server(debug=True)