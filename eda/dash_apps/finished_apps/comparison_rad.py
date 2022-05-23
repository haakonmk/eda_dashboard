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



app = DjangoDash('Comparison_Radiation', external_stylesheets= [dbc.themes.BOOTSTRAP])
path = "/Users/hakonkolsto/Documents/django/djangoProject/eda/polls/input_files/"

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
         dcc.Graph(id='gcr', figure={}) ]),
         width = 6,
         )

col2 = dbc.Col(html.Div([
         dcc.Graph(id='saa', figure={}) ]),
         width = 6,
         )

col3 = dbc.Col(html.Div([
         dcc.Graph(id='total', figure={}) ]),
         width = 6,
         )

col4 = dbc.Col(html.Div([
        dcc.Graph(id='acc', figure={})]),
        width = 6,
        )

app.layout = html.Div(
    [
        dbc.Row([colMission]),
        dbc.Row([col1, col2]),
        html.Br(),
        dbc.Row([col3, col4]),
        dcc.Store(id='dataframe'), #Store the data
        dcc.Store(id='store_selected_values'), #Store the data
    ]
)


store_checklist = []
dict_store = {}
seconds_to_days =  1/86400

def clean_data(mission_id):
    """Returns temperature (ISS/Ground) and days after launch for a given mission"""
    df_launch = pd.read_json(path + '{}_Radiation_CSV.json'.format(mission_id))
    df_launch.set_index('Date', inplace=True)
    df_launch['Accumulated_Radiation'] = df_launch['Total_Dose_mGy_d'].cumsum()
    days_after_launch_col = (df_launch.index -df_launch.index[0]).total_seconds()*seconds_to_days
    mission_dict = {mission_id : np.array([days_after_launch_col.values, df_launch['GCR_Dose_mGy_d'].values, df_launch['SAA_Dose_mGy_d'].values,
                    df_launch['Total_Dose_mGy_d'].values, df_launch['Accumulated_Radiation'].values])}
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
    [Output(component_id='gcr', component_property='figure'),
    Output(component_id='saa', component_property='figure'),
    Output(component_id='total', component_property='figure'),
    Output(component_id='acc', component_property='figure')],
    [Input("dataframe", "data"),
    Input(component_id='checklist_mission', component_property='value')]
)

def update_homescreen(dict_plot, checklist):
    fig1 = fig_plot_line(dict_plot, checklist,'GCR')
    fig2 = fig_plot_line(dict_plot, checklist,'SAA')
    fig3 = fig_plot_line(dict_plot, checklist,'Total')
    fig4 = fig_plot_line(dict_plot, checklist,'Accumulated')

    return fig1, fig2, fig3, fig4

def fig_plot_line(dict, checklist, choice):
    fig = go.Figure()
    if choice == 'GCR':
        index = 1
        title = 'Galactic Cosmic Ray (GCR) Radiation Dose'
        ytitle = 'GCR Dose [mGy/day]'
    elif choice  == 'SAA':
        index = 2
        title = 'South Atlantic Anomaly (SAA) Radiation Dose'
        ytitle = 'SAA Dose [mGy/day]'
    elif choice  == 'Total':
        index = 3
        title = 'Total Radiation Dose'
        ytitle = 'Total Dose [mGy/day]'
    elif choice  == 'Accumulated':
        index = 4
        title = 'Accumulated Radiation Dose'
        ytitle = 'Dose [mGy]'
    for key in checklist:
        fig.add_trace(go.Scatter(x=dict[key][0], y=dict[key][index],
                     mode='lines',
                     name=key))
    fig.layout.template = 'plotly_dark'
    fig.update_layout(
    xaxis_title="Days After Launch",
    yaxis_title=ytitle,
    legend_title="Mission",
    title={
        'text': title,
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}
        )
    return fig
