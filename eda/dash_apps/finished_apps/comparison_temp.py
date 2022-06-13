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


df_eda = pd.read_json(path + '{}_CSV.json'.format(mission.item()))
df_eda_init = df_eda.head()
# Callback connects the Dash components to Plotly graphs

colMission = dbc.Col(html.Div([ dbc.Card(
                [
                    dbc.CardHeader("Mission Selection", style = {'textAlign' : 'center'}),
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
        html.H5(id = 'data_status'),
        dbc.Row([col3]),
        dbc.Row([col1]),
        dcc.Store(id='dataframe'), #Store the data
        dcc.Store(id='store_selected_values'), #Store the data
        dcc.Store(id='empty_data_id'), #Store the data
    ]
)


store_checklist = []
no_data_list = []
dict_store = {}
seconds_to_days =  1/86400

def load_data(mission):
    try:
        df = pd.read_json(path + '{}_CSV.json'.format(mission))
        return df, ""
    except ValueError:
        df = df_eda_init.copy()
        for col in df.columns:
            df[col].values[:] = 0
        return df, "Data not available."


def clean_data(mission_id):
    """Returns temperature (ISS/Ground) and days after launch for a given mission"""
    df_tmp, data_status_eda = load_data(mission_id)
    df_tmp.Controller_Time_GMT = pd.to_datetime(df_tmp.Controller_Time_GMT)
    df_tmp.set_index('Controller_Time_GMT', inplace=True)
    if len(data_status_eda) == 0:
        l = df_tmp[df_tmp['Mission_Milestone'] == 'Launch'].index
        df_launch = df_tmp.loc[l[0]:]
        days_after_launch_col = (df_launch.index -l[0]).total_seconds()*seconds_to_days
        mission_dict = {mission_id : np.array([days_after_launch_col.values, df_launch['Temp_degC_Ground'].values, df_launch['Temp_degC_ISS'].values])}
    else:
        mission_dict = {mission_id : np.array([0, 0, 0])}
    return mission_dict, data_status_eda


@app.callback(
    [Output("store_selected_values", "data"),
    Output("dataframe", "data"),
    Output("empty_data_id", "data")],
    Input(component_id='checklist_mission', component_property='value'),
    )

def update_dataframe(checklist):
    store_checklist.extend(checklist)
    updated_checklist = np.unique(store_checklist).tolist()
    for mission_id in updated_checklist:
        if mission_id not in dict_store.keys():
            mission_dict, data_status_eda = clean_data(mission_id)
            if len(data_status_eda) == 0:
                dict_store.update(mission_dict)
            else:
                if mission_id not in no_data_list:
                    no_data_list.append(mission_id)
    if len(no_data_list) > 0:
        for mission_id in no_data_list:
            try:
                store_checklist.remove(mission_id)
                updated_checklist.remove(mission_id)
            except ValueError:
                continue

    return updated_checklist, dict_store,  np.unique(no_data_list).tolist()



@app.callback(
    [Output(component_id='temperature_map_ground', component_property='figure'),
    Output(component_id='temperature_map_iss', component_property='figure')],
    [Input("dataframe", "data"),
    Input(component_id='checklist_mission', component_property='value'),
    Input('empty_data_id', 'data')]
)

def update_homescreen(dict_plot, checklist, no_data_list):
    plot_checklist = []
    for check in checklist:
        if check in list(dict_plot.keys()):
            plot_checklist.append(check)
    fig1 = fig_plot_line(dict_plot, plot_checklist,'Ground')
    fig2 = fig_plot_line(dict_plot, plot_checklist,'ISS')
    return fig1, fig2


@app.callback(
    Output(component_id='data_status', component_property='children'),
    [Input(component_id='checklist_mission', component_property='value'),
    Input(component_id='empty_data_id', component_property='data')]
    )

def display_data_status(checklist, no_data_list):
    selected_no_data = []
    for check in checklist:
        if check in no_data_list:
            selected_no_data.append(check)

    if len(selected_no_data) == 0:
        return ""
    elif len(selected_no_data) == 1:
        return "Data for selected mission " + " ".join(selected_no_data) + " is not available."
    else:
        return "Data for selected missions " + ", ".join(selected_no_data) + " are not available."



def fig_plot_line(dict, checklist, location):
    fig = go.Figure()
    if location == 'Ground':
        index = 1
    elif location  == 'ISS':
        index = 2
    for key in checklist:
        fig.add_trace(go.Scattergl(x=dict[key][0], y=dict[key][index],
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
