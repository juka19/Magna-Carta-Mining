import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from pickle import load
import networkx as nx
import re

with open('data/data_cleaned.pickle', 'rb') as handle:
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
    ),
    paper_bgcolor='rgba(0,0,0,0)', # transparent background
    plot_bgcolor='rgba(0,0,0,0)', # transparent 2nd background
    xaxis =  {'showgrid': False, 'zeroline': False}, # no gridlines
    yaxis = {'showgrid': False, 'zeroline': False}, # no gridlines
)
fig1.update_traces(
    hovertemplate="<br>".join([
        "Year: %{x}",
        "Cases: %{y}"
    ])
)

pio.write_json(fig1, 'output/plotly_bycountry.json')

fig2 = pio.read_json('output/plotly_bycountry.json')

# network graph


nodes = [(re.findall('\d{3,5}\/\d{2}', row)[0], l, c, y, t.replace('(1 of 1)', '')) for row, l, c, y, t in zip(df['ident'], df['related_cases'], df['respondent_state'], df['year'], df['title']) if re.findall('\d{3,5}\/\d{2}', row)]

G = nx.Graph()
for node in nodes:
    if node[0] not in G:
        G.add_node(node[0], country=node[2], year=node[3], title=node[4],  size = 1)
        if node[1]:
            for i in node[1]:
                if G.has_edge(node[0], i):
                    G[node[0]][i]['weight'] += 1
                else:
                    G.add_edge(node[0], i, weight=1)
    
G.remove_nodes_from(list(nx.isolates(G)))
 
for node in list(G.nodes):
    if len(G.edges(node)) < 5:
        G.remove_node(node)

pos_ = nx.spring_layout(G)

def make_edge(x, y, text, width):
    return  go.Scatter(x = x,
                       y = y,
                       line = dict(width = width,
                                   color = 'cornflowerblue'),
                       hoverinfo = 'text',
                       text = ([text]),
                       mode = 'lines')

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

tooltip = []
for node in G.nodes:
    tooltip.append("<br>".join([
        f"{G.nodes[node]['title']}",
        f"{G.nodes[node]['year']}"
    ]) if G.nodes[node] else 'not in Grand Chamber')

node_trace = go.Scatter(x = [],
                        y = [],
                        text = [],
                        textposition = "top center",
                        textfont_size = 10,
                        mode = 'markers+text',
                        hovertext = tooltip,
                        hoverinfo = "text",
                        marker = dict(color = [],
                                         size = [],
                                         line = None))

for node in G.nodes:
    x, y = pos_[node]
    node_trace['x'] += tuple([x])
    node_trace['y'] += tuple([y])
    node_trace['marker']['color'] += tuple(['CadetBlue'])
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
n = 1
for trace in edge_trace:
    fig.add_trace(trace)
    print(f"Added edge {n} of {len(edge_trace)}")
    n += 1

fig.add_trace(node_trace)
fig.update_layout(showlegend = False) 
fig.update_xaxes(showticklabels = False)
fig.update_yaxes(showticklabels = False)

fig.show()

pio.write_json(fig, 'output/plotly_network.json')

# Creating confusion matrix

with open('data/cm.pickle', 'rb') as handle:
    cm = load(handle)

