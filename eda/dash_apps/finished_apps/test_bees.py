from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
import plotly.express as px
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('Bees', external_stylesheets= [dbc.themes.BOOTSTRAP]
)

df = pd.read_csv('/Users/hakonkolsto/Downloads/intro_bees.csv')
df = df.groupby(['State', 'ANSI', 'Affected by', 'Year', 'state_code'])[['Pct of Colonies Impacted']].mean()
df.reset_index(inplace=True)
print(df[:5])

# Dropdown is list of things affecting bees
bee_killers = pd.unique(df['Affected by'])


col1 = dbc.Col(html.Div([
        dcc.Dropdown(id="slct_impact1",
                     options=[{"label": x, "value":x} for x in bee_killers],
                     value="Pesticides",
                     multi=False,
                     style={'width': "70%"}
                     ),
        html.Div(id='output_container1', children=[]),
        html.Br(),
        dcc.Graph(id='my_bee_map1', figure={})]), width = 4 )


col2 = dbc.Col(html.Div([
        dcc.Dropdown(id="slct_impact2",
                     options=[{"label": x, "value":x} for x in bee_killers],
                     value="Pesticides",
                     multi=False,
                     style={'width': "70%"}
                     ),
        html.Div(id='output_container2', children=[]),
        html.Br(),
        dcc.Graph(id='my_bee_map2', figure={})
    ]), width = 4)


col3 = dbc.Col(html.Div([
        dcc.Dropdown(id="slct_impact3",
                     options=[{"label": x, "value":x} for x in bee_killers],
                     value="Pesticides",
                     multi=False,
                     style={'width': "70%"}
                     ),

        html.Div(id='output_container3', children=[]),
        html.Br(),
        dcc.Graph(id='my_bee_map3', figure={})
    ]), width = 4)


app.layout = html.Div(
    [
        dbc.Row([ col1, col2, col3])
    ]
)

# Callback connects the Dash components to Plotly graphs

@app.callback(
    [Output(component_id='output_container1', component_property='children'),
     Output(component_id='my_bee_map1', component_property='figure')],
    [Input(component_id='slct_impact1', component_property='value')]
)

@app.callback(
    [Output(component_id='output_container2', component_property='children'),
     Output(component_id='my_bee_map2', component_property='figure')],
    [Input(component_id='slct_impact2', component_property='value')]
)
@app.callback(
    [Output(component_id='output_container3', component_property='children'),
     Output(component_id='my_bee_map3', component_property='figure')],
    [Input(component_id='slct_impact3', component_property='value')]
)



def update_graph(option_slctd):
    """ X should represent year, y: % of bee colonies. Color: State"""
    container = "The year chosen was: {}".format(option_slctd)
    print(option_slctd)
    dff = df.copy()
    dff = dff[dff['Affected by'] == option_slctd]
    dff = dff[(dff["State"] == "Idaho") | (dff["State"] == "New York") | (dff["State"] == "New Mexico")]


    fig = px.line(
        data_frame=dff,
        x='Year',
        y='Pct of Colonies Impacted',
        color='State',
        template='plotly_dark'
        #template='seaborn'
    )
    return container, fig
