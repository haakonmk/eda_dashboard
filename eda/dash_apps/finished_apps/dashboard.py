from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd
import plotly.express as px
import os, sys, re, glob

numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts



app = DjangoDash('Overview', external_stylesheets= [dbc.themes.BOOTSTRAP])
path = "/Users/hakonkolsto/Documents/django/djangoProject/eda/polls/input_files/"

mission_info = pd.read_csv(path + "mission_info.csv")
mission_slctd = 'Rodent Research 1 (SpaceX-4)'
mission = mission_info[mission_info['Title'] == mission_slctd]['Mission']

df_eda = pd.read_json(path + '{}_CSV.json'.format(mission.item()))
df_rad = pd.read_json(path + '{}_Radiation_CSV.json'.format(mission.item()))

df_eda_init = df_eda.head()
df_rad_init = df_rad.head()

#radiation_files = sorted(glob.glob(path + "RR*_Ra*_CSV.json"), key=numericalSort)
#eda_files = sorted(glob.glob(path + "RR?_CSV.json"), key=numericalSort)
light_listInit = [key for key in df_eda.keys() if key[0:3] == 'Lig']
default_options = [{"label": light , "value": light} for light in light_listInit]
default_milestone_options = [{"label": "  Mission Milestones", "value": "true"}]

# Callback connects the Dash components to Plotly graphs

col = dbc.Col(html.Div([
        dcc.Dropdown(id="mission_slct",
                     options=mission_info['Title'],
                     value='Rodent Research 1 (SpaceX-4)',
                     multi=False,
                     style={'width': "60%", 'justify-content': 'center'},
                     ), html.H5(id = 'data_status_eda'),
        html.Div(children=html.Strong('Mission Description'), style = {'textAlign' : 'center', 'backgroundColor': '#c2ccd6'}),
        html.Div(id='mission_description', children=[], style = {'textAlign' : 'left', 'backgroundColor': '#f0f2f5'}), #e1e5ea
        #html.Div(id='mission_description', children=[]),
        #html.Div(id='mission_link', children=[]),
        html.Br()]), width = 12)

colMission = dbc.Col(html.Div([ dbc.Card(
                [
                    dbc.CardHeader("Mission Milestone Dates", style = {'textAlign' : 'center'}),
                    dbc.CardBody(
                        [dcc.Markdown(id='milestone_description', children=[], style = {'textAlign' : 'center'}), #e1e5ea
                        html.Div(id ="milestone_output", style = {'textAlign' : 'center'}),
                        dcc.Checklist(
                            id="checklist_milestone",
                            inline=True,
                            style = {'textAlign' : 'center'},
                            labelStyle={"display": "block"},

                        ),
                        html.Div(id ="light_output", style = {'textAlign' : 'center'}),
                        dcc.Checklist(
                            id="checklist_lights",
                            options=default_options,
                            inline=True,
                            #labelStyle={"display": "block"},
                            style = {'textAlign' : 'center'},
                            inputStyle={"margin-right": "5px"},
                        ),
                        ]
                    ),
                ]
            )
            ]), width = 3)

# Row 2
col1 = dbc.Col(html.Div([
         dcc.Graph(id='temperature_map', figure={}) ]),
         width = 6
         )

col2 = dbc.Col(html.Div([
        dcc.Graph(id='co2_map', figure={})]),
        width = 6
        )


col4 = dbc.Col(html.Div([
        dcc.Graph(id='rh1_map', figure={})]),
        width = 9
        )


col1_rad = dbc.Col(html.Div([
         dcc.Graph(id='gcr_map', figure={}) ]),
         width = 4
         )

col2_rad = dbc.Col(html.Div([
        dcc.Graph(id='saa_map', figure={})]),
        width = 4
        )

col3_rad = dbc.Col(html.Div([
        dcc.Graph(id='tot_map', figure={})]),
        width = 4
        )

col4_rad = dbc.Col(html.Div([
        dcc.Graph(id='all_map', figure={})]),
        width = 5
        )

col5_rad = dbc.Col(html.Div([
        dcc.Graph(id='acc_map', figure={})]),
        width = 7
        )




app.layout = html.Div(
    [
        dbc.Row([col]),
        dbc.Row([col1, col2]),
        html.Br(),
        dbc.Row([colMission, col4]),# justify="center"),
        html.Br(),
        html.H3(children='Radiation Data'),
        html.H5(id = 'data_status_rad'),
        dbc.Row([col1_rad, col2_rad, col3_rad]),
        html.Br(),
        dbc.Row([col4_rad, col5_rad ]),
        dcc.Store(id='dataframe_eda'), #Store the data
        dcc.Store(id='dataframe_rad'), #Store the data
        dcc.Store(id='data_availability_eda'), #Store the data
        dcc.Store(id='data_availability_rad'), #Store the data
    ]
)



@app.callback([Output(component_id='data_status_eda', component_property='children'),
                Output(component_id='data_status_rad', component_property='children')],
                [Input(component_id='data_availability_eda', component_property='data'),
                Input(component_id='data_availability_rad', component_property='data')]
                )
def display_data_status(data_availability_eda,data_availability_rad):
    return data_availability_eda, data_availability_rad


# Checks the data availability

def load_data(mission, radiation = False):
    try:
        if radiation:
            df = pd.read_json(path + '{}_Radiation_CSV.json'.format(mission.item()))
        else:
            df = pd.read_json(path + '{}_CSV.json'.format(mission.item()))
        return df, ""
    except ValueError:
        if radiation:
            df = df_rad_init.copy()
        else:
            df = df_eda_init.copy()
        for col in df.columns:
            df[col].values[:] = 0
        return df, "Data not available."




@app.callback([Output('dataframe_eda', 'data'), Output('dataframe_rad', 'data'),
               Output(component_id='mission_description', component_property='children'),
               Output(component_id='milestone_description', component_property='children'),
               Output(component_id='light_output', component_property='children'),
               Output(component_id='checklist_lights', component_property='options'),
               Output(component_id='milestone_output', component_property='children'),
               Output(component_id='checklist_milestone', component_property='options'),
               Output(component_id='data_availability_eda', component_property='data'),
               Output(component_id='data_availability_rad', component_property='data')],
               [Input('mission_slct', 'value')])

def clean_and_extract_metadata(mission_slctd):
    #mission_slctd = 'Rodent Research 1 (SpaceX-4)'
    mission = mission_info[mission_info['Title'] == mission_slctd]['Mission']
    mission_description = mission_info[mission_info['Title'] == mission_slctd]['Description'].item()
    # View info
    df_eda, data_status_eda = load_data(mission)
    df_rad, data_status_rad = load_data(mission, True)
    df_eda.Controller_Time_GMT = pd.to_datetime(df_eda.Controller_Time_GMT)
    df_rad['Accumulated_Radiation'] = df_rad['Total_Dose_mGy_d'].cumsum()
    if len(data_status_eda) < len(data_status_rad):
        milestone_description = mission_milestones(df_eda)
    elif len(data_status_eda) > len(data_status_rad):
        milestone_description = mission_milestones(df_rad, True)
    elif len(data_status_eda) == 0 and len(data_status_rad)== 0:
        milestone_description = mission_milestones(df_eda)
    else:
        milestone_description = "No data available"
    light_list = [key for key in df_eda.keys() if key[0:3] == 'Lig']
    if df_eda[df_eda.keys()[0]].dt.year[0]== 1970:
        light_list = []

    if df_eda[df_eda.keys()[0]].dt.year[0]== 1970 and df_rad[df_rad.keys()[0]].dt.year[0]== 1970:
        milestone_output_string = html.Strong('')
        checklist_milestone_val = []
    else:
        milestone_output_string = html.Strong('Display Milestone')
        checklist_milestone_val = default_milestone_options

    if len(light_list) > 0:
        light_output_string = html.Strong('Display Lights')
        options = [{"label": light , "value": light} for light in light_list]
    else:
        chklst_lights_val = []
        light_output_string = html.Strong('')
        options = []
    return df_eda.to_json(date_format='iso', orient='split'), df_rad.to_json(date_format='iso', orient='split'), \
    mission_description, milestone_description, light_output_string, options, milestone_output_string, \
    checklist_milestone_val, data_status_eda, data_status_rad



@app.callback([Output(component_id='temperature_map', component_property='figure'),
            Output(component_id='co2_map', component_property='figure'),
            Output(component_id='rh1_map', component_property='figure')],
            [Input('dataframe_eda', 'data'),
            Input(component_id='checklist_milestone', component_property='value'),
            Input(component_id='checklist_lights', component_property='value'),
            Input(component_id='data_availability_eda', component_property='data')]
            )


def update_homescreen(json_data, chklst_milst_val, chklst_lights_val, data_status_eda):
    #mission_slctd = 'Rodent Research 1 (SpaceX-4)'
    df_eda = pd.read_json(json_data, orient='split')
    fig1 = px.line(data_frame=df_eda, x='Controller_Time_GMT', y=['Temp_degC_Ground', 'Temp_degC_ISS'], template='plotly_dark')
    
    fig1.update_xaxes(nticks=10)
    fig1.update_layout(title_text='Temperature', title_x=0.5,
                        yaxis={"title": "Degrees [C]"}, legend={"title":"Location"},
                        xaxis={"title":"Date [MM/DD/YY HH:mm]"})
    newnames = {'Temp_degC_Ground':'Ground', 'Temp_degC_ISS': 'ISS'}
    fig1.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                        legendgroup = newnames[t.name],
                                        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))


    fig2 = px.line(data_frame=df_eda, x='Controller_Time_GMT', y=['CO2_ppm_Ground', 'CO2_ppm_ISS'], template='plotly_dark')
    fig2.update_xaxes(nticks=10)
    fig2.update_layout(title_text='CO2', title_x=0.5,
                        yaxis={"title": "CO2 [ppm]"}, legend={"title":"Location"},
                        xaxis={"title":"Date [MM/DD/YY HH:mm]"})
    newnames = {'CO2_ppm_Ground':'Ground', 'CO2_ppm_ISS': 'ISS'}
    fig2.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                        legendgroup = newnames[t.name],
                                        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

    fig3 = px.line(data_frame=df_eda, x='Controller_Time_GMT', y=['RH_percent_Ground', 'RH_percent_ISS'], template='plotly_dark')
    fig3.update_xaxes(nticks=10)
    fig3.update_layout(title_text='Relative Humidity', title_x=0.5,
                        yaxis={"title": "RH [%]"}, legend={"title":"Location"},
                        xaxis={"title":"Date [MM/DD/YY HH:mm]"})
    newnames = {'RH_percent_Ground':'Ground', 'RH_percent_ISS': 'ISS'}
    fig3.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                        legendgroup = newnames[t.name],
                                        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

    if chklst_lights_val != None:
        if len(data_status_eda) == 0:
            for lght in chklst_lights_val:
                draw_rectangel_light(df_eda, lght, [fig1, fig2, fig3])

    if chklst_milst_val == ['true']:
        if len(data_status_eda) == 0:
            draw_vertical_lines_mission_chcklist(df_eda, [fig1, fig2, fig3])

    return fig1, fig2, fig3



####################################################################
####################################################################
################ Radiation section of the dashboard ################
####################################################################
####################################################################

@app.callback(
    [Output(component_id='gcr_map', component_property='figure'),
    Output(component_id='saa_map', component_property='figure'),
    Output(component_id='tot_map', component_property='figure'),
    Output(component_id='all_map', component_property='figure'),
    Output(component_id='acc_map', component_property='figure')],
     [Input('dataframe_eda', 'data'), Input('dataframe_rad', 'data'),
     Input(component_id='checklist_milestone', component_property='value'),
     Input(component_id='checklist_lights', component_property='value'),
     Input(component_id='data_availability_rad', component_property='data'),
     Input(component_id='data_availability_eda', component_property='data')]
)

def update_homescreen_rad(df_eda, df_rad, chklst_milst_val, chklst_lights_val, data_status_rad, data_status_eda):
    #mission_slctd = 'Rodent Research 1 (SpaceX-4)'
    df_eda = pd.read_json(df_eda, orient='split')
    df_rad = pd.read_json(df_rad, orient='split')

    fig1 = px.line(data_frame=df_rad, x='Date', y=['GCR_Dose_mGy_d'], template='plotly_dark')
    fig1.update_xaxes(nticks=10)
    fig1.update_layout(title_text='Galactic Cosmic Ray (GCR) Radiation Dose', title_x=0.5,
                        yaxis={"title": "GCR Dose [mGy/day]"}, showlegend=False,
                        xaxis={"title":"Date [MM/DD/YY HH:mm]"})

    fig2 = px.line(data_frame=df_rad, x='Date', y=['SAA_Dose_mGy_d'],  template='plotly_dark', color_discrete_map={'SAA_Dose_mGy_d':'#EF553B'})
    fig2.update_xaxes(nticks=10)
    fig2.update_layout(title_text='South Atlantic Anomaly (SAA) Radiation Dose', title_x=0.5,
                        yaxis={"title": "SAA Dose [mGy/day]"}, showlegend=False,
                        xaxis={"title":"Date [MM/DD/YY HH:mm]"})

    fig3 = px.line(data_frame=df_rad, x='Date', y=['Total_Dose_mGy_d'], template='plotly_dark', color_discrete_map={'Total_Dose_mGy_d':'#00cc96'})
    fig3.update_xaxes(nticks=10)
    fig3.update_layout(title_text='Total Radiation Dose', title_x=0.5,
                        yaxis={"title": "Total Dose [mGy/day]"}, showlegend=False,
                        xaxis={"title":"Date [MM/DD/YY HH:mm]"})

    fig4 = px.line(data_frame=df_rad, x='Date', y=['GCR_Dose_mGy_d', 'SAA_Dose_mGy_d', 'Total_Dose_mGy_d' ], template='plotly_dark')
    fig4.update_xaxes(nticks=10)
    fig4.update_layout(title_text='Radiation Dose', title_x=0.5,
                        yaxis={"title": "Dose [mGy/day]"},  legend={"title":"Dose"},
                        xaxis={"title":"Date [MM/DD/YY HH:mm]"})
    newnames = {'Total_Dose_mGy_d':'Total', 'GCR_Dose_mGy_d': 'GCR', 'SAA_Dose_mGy_d': 'SAA'}
    fig4.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                        legendgroup = newnames[t.name],
                                        hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

    fig5 = px.line(data_frame=df_rad, x='Date', y=['Accumulated_Radiation' ], template='plotly_dark')
    fig5.update_xaxes(nticks=10)
    fig5.update_layout(title_text='Accumulated Radiation Dose', title_x=0.5,
        yaxis={"title": "Dose [mGy]"},  showlegend=False,
        xaxis={"title":"Date [MM/DD/YY HH:mm]"})
    newnames = {'Accumulated_Radiation':'Accumulated'}
    fig5.for_each_trace(lambda t: t.update(name = newnames[t.name],
                                    legendgroup = newnames[t.name],
                                    hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))


    if chklst_lights_val != None:
        if len(data_status_rad) == 0 and len(data_status_eda) == 0:
            for lght in chklst_lights_val:
                draw_rectangel_light(df_eda, lght, [fig1, fig2, fig3,fig4, fig5])

    if chklst_milst_val == ['true']:
        if len(data_status_rad) == 0:
            draw_vertical_lines_mission_chcklist(df_rad, [fig1, fig2, fig3,fig4, fig5], True)

    return fig1, fig2, fig3, fig4, fig5




def mission_milestones(df, radiation = False):
    if radiation:
        key = 'Date'
    else:
        key = 'Controller_Time_GMT'
    milestones = pd.unique(df['Mission_Milestone'])
    # Clean the stones
    info_string = "> \n\n \n \n"
    for milestone in milestones:
        if len(milestone) > 0:
            milestone_date = df[df['Mission_Milestone'] == milestone][key].astype(str).item()
            info_string += "> **{}** : *{}* \n\n".format(milestone, milestone_date)
    return info_string



def draw_vertical_lines_mission_chcklist(df, figList, radiation = False):
    milestones = pd.unique(df['Mission_Milestone'])
    if radiation:
        key = 'Date'
    else:
        key = 'Controller_Time_GMT'
    for milestone in milestones:
        if len(milestone) > 0:
            milestone_date = df[df['Mission_Milestone'] == milestone][key].astype(str).item()
            for fig in figList:
                fig.add_vline(x=milestone_date, line_width=2, line_dash="dash", line_color="orange")# for milestone_date in milestone_dates]
                fig.add_annotation(x=milestone_date, y =1 , yref="paper", text=milestone, bgcolor = "orange", hovertext = milestone_date)


def draw_rectangel_light(df, lght, figList):
    time_intervals = []
    for i in range(1, len(df[lght])):
        if df[lght][i-1] != 'On' and df[lght][i] == 'On':
            start_interval = df['Controller_Time_GMT'][i]
        elif i == 1 and df[lght][i-1] == 'On':
            start_interval = df['Controller_Time_GMT'][i-1]
        elif df[lght][i-1] == 'On' and df[lght][i] != 'On':
            if df[lght][i-5] == 'On':
                end_interval = df['Controller_Time_GMT'][i-1]
                time_intervals.append([start_interval, end_interval])

    for deltaT in time_intervals:
        for fig in figList:
            fig.add_vrect(x0=deltaT[0], x1=deltaT[1], fillcolor="yellow", opacity=0.25, line_width=0, annotation_text=lght, annotation_position="top left",)
            #fig.add_annotation(x=milestone_date, y =1 , yref="paper", text=lght, bgcolor = "orange", hovertext = lght)
