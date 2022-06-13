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
path = "polls/input_files/"

mission_info = pd.read_csv(path + "mission_info.csv")
mission_slctd = 'Rodent Research 1 (SpaceX-4)'
mission = mission_info[mission_info['Title'] == mission_slctd]['Mission']

df_eda = pd.read_json(path + '{}_CSV.json'.format(mission.item()))
df_rad = pd.read_json(path + '{}_Radiation_CSV.json'.format(mission.item()))

df_eda_init = df_eda.head()
df_rad_init = df_rad.head()

# Callback connects the Dash components to Plotly graphs

colMission = dbc.Col(html.Div([ dbc.Card(
                [
                    dbc.CardHeader("Missions", style = {'textAlign' : 'center'}),
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
        html.H5(id = 'data_status'),
        dbc.Row([col1, col2]),
        html.Br(),
        dbc.Row([col3, col4]),
        dcc.Store(id='dataframe'), #Store the data
        dcc.Store(id='store_selected_values'),
        dcc.Store(id='empty_data_id'), #Store the data


    ]
)


store_checklist = []
no_data_list = []
dict_store = {}
seconds_to_days =  1/86400


def load_data(mission):
    try:
        df = pd.read_json(path + '{}_Radiation_CSV.json'.format(mission))
        return df, ""
    except ValueError:
        df = df_rad_init.copy()
        for col in df.columns:
            df[col].values[:] = 0
        return df, "Data not available."

def clean_data(mission_id):
    """Returns temperature (ISS/Ground) and days after launch for a given mission"""
    df_launch, data_status_rad = load_data(mission_id)
    df_launch.set_index('Date', inplace=True)
    df_launch['Accumulated_Radiation'] = df_launch['Total_Dose_mGy_d'].cumsum()
    days_after_launch_col = (df_launch.index -df_launch.index[0]).total_seconds()*seconds_to_days
    mission_dict = {mission_id : np.array([days_after_launch_col.values, df_launch['GCR_Dose_mGy_d'].values, df_launch['SAA_Dose_mGy_d'].values,
                    df_launch['Total_Dose_mGy_d'].values, df_launch['Accumulated_Radiation'].values])}
    return mission_dict, data_status_rad

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
            mission_dict, data_status_rad = clean_data(mission_id)
            print("{} {}".format(len(data_status_rad), mission_id ))
            if len(data_status_rad) == 0:
                dict_store.update(mission_dict)
            else:
                if mission_id not in no_data_list:
                    no_data_list.append(mission_id)
                    #updated_checklist.remove(mission_id)
                    #print("AF rem {}".format(updated_checklist))
        else:
            print('Data already loaded!')
    if len(no_data_list) > 0:
        for mission_id in no_data_list:
            print(mission_id)
            try:
                store_checklist.remove(mission_id)
                updated_checklist.remove(mission_id)
            except ValueError:
                continue
    print('no_data_list: {}'.format(no_data_list))
    return updated_checklist, dict_store, np.unique(no_data_list).tolist()

@app.callback(
    [Output(component_id='gcr', component_property='figure'),
    Output(component_id='saa', component_property='figure'),
    Output(component_id='total', component_property='figure'),
    Output(component_id='acc', component_property='figure')],
    [Input("dataframe", "data"),
    Input(component_id='checklist_mission', component_property='value'),
    Input('empty_data_id', 'data')]
)

def update_homescreen(dict_plot, checklist, no_data_list):
    plot_checklist = []
    for check in checklist:
        if check in list(dict_plot.keys()):
            plot_checklist.append(check)
    fig1 = fig_plot_line(dict_plot, plot_checklist,'GCR')
    fig2 = fig_plot_line(dict_plot, plot_checklist,'SAA')
    fig3 = fig_plot_line(dict_plot, plot_checklist,'Total')
    fig4 = fig_plot_line(dict_plot, plot_checklist,'Accumulated')

    return fig1, fig2, fig3, fig4

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
        fig.add_trace(go.Scattergl(x=dict[key][0], y=dict[key][index],
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
