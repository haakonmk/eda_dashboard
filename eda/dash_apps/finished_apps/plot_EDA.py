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



app = DjangoDash('EDA', external_stylesheets= [dbc.themes.BOOTSTRAP])
path = "/Users/hakonkolsto/Documents/django/djangoProject/eda/polls/input_files/"

# Just initialize some stuff
mission_info = pd.read_csv(path + "mission_info.csv")
mission_slctd = 'Rodent Research 1 (SpaceX-4)'
mission = mission_info[mission_info['Title'] == mission_slctd]['Mission']
df_eda = pd.read_json(path + '{}_CSV.json'.format(mission.item()))
#radiation_files = sorted(glob.glob(path + "RR*_Ra*_CSV.json"), key=numericalSort)
#eda_files = sorted(glob.glob(path + "RR?_CSV.json"), key=numericalSort)
light_listInit = [key for key in df_eda.keys() if key[0:3] == 'Lig']
default_options = [{"label": light , "value": light} for light in light_listInit]

#hfaifhih
# Callback connects the Dash components to Plotly graphs

col = dbc.Col(html.Div([
        dcc.Dropdown(id="mission_slct",
                     options=mission_info['Title'],
                     value='Rodent Research 1 (SpaceX-4)',
                     multi=False,
                     style={'width': "60%", 'justify-content': 'center'},
                     ),
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
                        html.Div(children=html.Strong('Display Milestone'), style = {'textAlign' : 'center'}),
                        dcc.Checklist(
                            id="checklist_milestone",
                            options=[
                                {"label": "  Mission Milestones", "value": "true"},
                            ],
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


# Provides the layout setup
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

app.layout = html.Div(
    [
        dbc.Row([col]),
        dbc.Row([col1, col2]),
        html.Br(),
        dbc.Row([colMission, col4]),# justify="center"),

        dcc.Store(id='dataframe'), #Store the data
    ]
)

@app.callback([Output('dataframe', 'data'),
               Output(component_id='mission_description', component_property='children'),
               Output(component_id='milestone_description', component_property='children')],
               [Input('mission_slct', 'value')])

def load_data(mission_slctd):
    """Returns dataframe and mission and milestone description"""
    mission = mission_info[mission_info['Title'] == mission_slctd]['Mission']
    # View info
    mission_description = mission_info[mission_info['Title'] == mission_slctd]['Description'].item()
    df_eda = pd.read_json(path + '{}_CSV.json'.format(mission.item()))
    df_eda.Controller_Time_GMT = pd.to_datetime(df_eda.Controller_Time_GMT)
    milestone_description = mission_milestones(df_eda)
    return df_eda.to_json(date_format='iso', orient='split'), mission_description, milestone_description


@app.callback([Output(component_id='temperature_map', component_property='figure'),
            Output(component_id='co2_map', component_property='figure'),
            Output(component_id='rh1_map', component_property='figure'),
            Output(component_id='light_output', component_property='children'),
            Output(component_id='checklist_lights', component_property='options')],
            [Input('dataframe', 'data'), Input(component_id='checklist_milestone', component_property='value'),
            Input(component_id='checklist_lights', component_property='value')]
            )


def update_homescreen(json_data, chklst_milst_val, chklst_lights_val):
    #mission_slctd = 'Rodent Research 1 (SpaceX-4)'
    df_eda = pd.read_json(json_data, orient='split')
    light_list = [key for key in df_eda.keys() if key[0:3] == 'Lig']
    # Some missions don't have Lights On/Off -
    if len(light_list) > 0:
        light_output_string = html.Strong('Display Lights')
        options = [{"label": light , "value": light} for light in light_list]
    else:
        chklst_lights_val = []
        light_output_string = html.Strong('')
        options = []
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
        for lght in chklst_lights_val:
            draw_rectangel_light(df_eda, lght, [fig1, fig2, fig3])

    if chklst_milst_val == ['true']:
        draw_vertical_lines_mission_chcklist(df_eda, [fig1, fig2, fig3])

    return fig1, fig2, fig3, light_output_string, options #, , mission_description, mission_link



def mission_milestones(df_eda):
    milestones = pd.unique(df_eda['Mission_Milestone'])
    # Clean the stones
    info_string = "> \n\n \n \n"
    for milestone in milestones:
        if len(milestone) > 0:
            milestone_date = df_eda[df_eda['Mission_Milestone'] == milestone]['Controller_Time_GMT'].astype(str).item()
            #print(milestone_date)
            info_string += "> **{}** : *{}* \n\n".format(milestone, milestone_date)
    return info_string



def draw_vertical_lines_mission_chcklist(df_eda, figList):
    milestones = pd.unique(df_eda['Mission_Milestone'])
    for milestone in milestones:
        if len(milestone) > 0:
            milestone_date = df_eda[df_eda['Mission_Milestone'] == milestone]['Controller_Time_GMT'].astype(str).item()
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
