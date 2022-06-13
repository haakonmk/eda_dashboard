from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
import plotly.express as px
import os, sys, re, glob
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'


numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts



app = DjangoDash('Comparison_Temperature', external_stylesheets= [dbc.themes.BOOTSTRAP])
path = "polls/input_files/"

mission_info = pd.read_csv(path + "mission_info.csv")
mission_slctd = 'Rodent Research 1 (SpaceX-4)'
mission = mission_info[mission_info['Title'] == mission_slctd]['Mission']

# Callback connects the Dash components to Plotly graphs

colMission = dbc.Col(html.Div([ dbc.Card(
                [
                    dbc.CardHeader("Mission Milestone Dates", style = {'textAlign' : 'center'}),
                    dbc.CardBody(
                        [html.Div(children=html.Strong('Select Missions to Compare'), style = {'textAlign' : 'center'}),
                        dcc.Checklist(
                            id="checklist_mission",
                            options=[{"label": mission_nr , "value": mission_nr} for mission_nr in mission_info['Mission']],
                            style = {'textAlign' : 'center'},
                            value=["RR1"],persistence = True,
                        ),
                        ]
                    ),
                ]
            )
            ]), width = 5)


col1 = dbc.Col(html.Div([
         dcc.Graph(id='temperature_map_ground', figure={}) ]),
         width = 12,
         )

col3 = dbc.Col(html.Div([
        dcc.Graph(id='temperature_map_iss', figure={})]),
        width = 12,
        )

app.layout = html.Div(
    [
        dbc.Row([colMission]),
        dbc.Row([col3]),
        html.Br(),
        dbc.Row([col1]),
        dcc.Store(id='dataframe'), #Store the data
        dcc.Store(id='store_selected_values'), #Store the data
    ]
)


store_checklist = []
dict_store = {}
seconds_to_days =  1/86400

def clean_data(mission_id):
    """Returns temperature (ISS/Ground) and days after launch for a given mission"""
    df_tmp = pd.read_json(path + '{}_CSV.json'.format(mission_id))
    df_tmp.Controller_Time_GMT = pd.to_datetime(df_tmp.Controller_Time_GMT)
    df_tmp.set_index('Controller_Time_GMT', inplace=True)
    l = df_tmp[df_tmp['Mission_Milestone'] == 'Launch'].index
    df_launch = df_tmp.loc[l[0]:]
    days_after_launch_col = (df_launch.index -l[0]).total_seconds()*seconds_to_days
    mission_dict = {mission_id : np.array([days_after_launch_col.values, df_launch['Temp_degC_Ground'].values, df_launch['Temp_degC_ISS'].values])}
    return mission_dict


@app.callback(
    [Output("store_selected_values", "data"),
    Output("dataframe", "data")],
    Input(component_id='checklist_mission', component_property='value'),
    )

def update_dataframe(checklist):
    store_checklist.extend(checklist)
    updated_checklist = np.unique(store_checklist).tolist()
    print(checklist)
    print(updated_checklist)
    for mission_id in updated_checklist:
        if mission_id not in dict_store.keys():
            mission_dict = clean_data(mission_id)
            dict_store.update(mission_dict)
            print(mission_id)
        else:
            print('Data already loaded!')
    print(dict_store.keys())
    return updated_checklist, dict_store



@app.callback(
    [Output(component_id='temperature_map_ground', component_property='figure'),
    Output(component_id='temperature_map_iss', component_property='figure')],
    [Input("dataframe", "data"),
    Input(component_id='checklist_mission', component_property='value')]
)

def update_homescreen(dict_plot, checklist ):
    fig1 = fig_plot_line(dict_plot, checklist,'Ground')
    fig2 = fig_plot_line(dict_plot, checklist,'ISS')
    return fig1, fig2


def fig_plot_line(dict, checklist, location):
    fig = go.Figure()
    if location == 'Ground':
        index = 1
    elif location  == 'ISS':
        index = 2
    for key in checklist:
        fig.add_trace(go.Scatter(x=dict[key][0], y=dict[key][index],
                     mode='lines',
                     name=key))
    fig.layout.template = 'plotly_dark'
    fig.update_layout(
    xaxis_title="Days After Launch",
    yaxis_title="Temperature [C]",
    legend_title="Mission",
    title={
        'text': "Temperature {}".format(location),
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
        )
    return fig
