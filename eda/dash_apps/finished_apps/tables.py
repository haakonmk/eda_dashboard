from dash import dcc
import dash_bootstrap_components as dbc
from dash import html, dash_table
from collections import OrderedDict
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = DjangoDash('EDATables', external_stylesheets=external_stylesheets)

# Prepare dataframe
path = "/Users/hakonkolsto/Documents/django/djangoProject/eda/polls/input_files/"
mission_info = pd.read_csv(path + "mission_info.csv")



col = dbc.Col(html.Div([
        dcc.Dropdown(id="mission_slct",
                     options=mission_info['Title'],
                     value='Rodent Research 1 (SpaceX-4)',
                     multi=False,
                     style={'width': "60%", 'justify-content': 'center'}

                     ),
                    #html.Div(id='mission_description', children=[]),
        #html.Div(id='mission_link', children=[]),
        html.Br()]), width = 12)



#def update_tablescreen(mission_slctd):



@app.callback(
    [Output(component_id='eda_table', component_property='children'),
    Output(component_id='rad_table', component_property='children'),
    Output(component_id='summary_table', component_property='children'),
    Output(component_id='milestone_description', component_property='children')],
     Input(component_id='mission_slct', component_property='value')
     )



def return_tables(mission_slctd):
    mission = mission_info[mission_info['Title'] == mission_slctd]['Mission']
    df_eda = pd.read_json(path + '{}_CSV.json'.format(mission.item()))
    df_eda.Controller_Time_GMT = pd.to_datetime(df_eda.Controller_Time_GMT)
    df_rad = pd.read_json(path + '{}_Radiation_CSV.json'.format(mission.item()))
    keys_update_eda = ['Controller_Time_GMT'] + [key for key in df_eda.keys() if key != 'Controller_Time_GMT']
    keys_update_rad = ['Date'] + [key for key in df_rad.keys() if key != 'Date']
    df_eda = df_eda[keys_update_eda]
    df_rad = df_rad[keys_update_rad]
    df_sum = manipulate_data(df_eda, df_rad)
    milestones = mission_milestones(df_eda)
    return return_tables(df_eda), return_tables(df_rad), return_tables(df_sum), milestones




def manipulate_data(df_eda, df_rad):
    var_list = ['Temp_degC_ISS', 'CO2_ppm_ISS', 'RH_percent_ISS', 'Temp_degC_Ground','CO2_ppm_Ground','RH_percent_Ground',
                'GCR_Dose_mGy_d', 'SAA_Dose_mGy_d', 'Total_Dose_mGy_d']
    var_list_name = ['Temperature [ISS]', 'CO2 [ISS]', 'Relative Humidity [ISS]',
                    'Temperature [Ground]', 'CO2 [Ground]', 'Relative Humidity [Ground]',
                    'Radiation: GCR', 'Radiation: SAA', 'Radiation: Total']
    df_concat = pd.concat([df_eda, df_rad], axis=1)
    gauge_dict= OrderedDict(
            [
            ('', var_list_name), ('Max', [round(df_concat[var].max(),3) for var in var_list]), ('Min', [round(df_concat[var].min(),3) for var in var_list]),
                ('Mean', [round(df_concat[var].min(),3) for var in var_list]), ('Standard deviation', [round(df_concat[var].std(),3) for var in var_list]),
                ('Median', [round(df_concat[var].median(),3) for var in var_list])
                ]
            )
    return pd.DataFrame(gauge_dict)


def mission_milestones(df_eda):
    milestones = pd.unique(df_eda['Mission_Milestone'])
    # Clean the stones
    info_string = "> \n\n \n \n"
    for milestone in milestones:
        if len(milestone) > 0:
            milestone_date = df_eda[df_eda['Mission_Milestone'] == milestone]['Controller_Time_GMT'].astype(str).item()
            info_string += "> **{}** : *{}* \n\n".format(milestone, milestone_date)
    return info_string



def return_tables(df):
    return dash_table.DataTable(df.to_dict('records'), style_cell_conditional=[
        {
            'if': {'column_id': c},
            'textAlign': 'left',
             'width': '12%'
        } for c in ['Date', 'Controller_Time_GMT','']
    ],
    style_data={
        'color': 'black',
        'backgroundColor': 'white'
    },
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(220, 220, 220)',
        }
    ],
    style_header={
        'backgroundColor': 'rgb(210, 210, 210)',
        'color': 'black',
        'fontWeight': 'bold'
    },
    columns=[{'id': c, 'name': c} for c in df.columns],
    page_size=10,
    #page_action='custom',
    fixed_rows={'headers': True},
    style_table={'height': '330px', 'overflowX': 'auto'},



    export_format ='csv',
)

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ],)
    ])



col_eda = dbc.Col(html.Div(id = 'eda_table'), width = 4)
col_summary = dbc.Col(html.Div(html.Div(id = 'summary_table', style={'width': '45%', 'display': 'inline-block'}),style={'display': 'flex'}))
colMission = dbc.Col(html.Div([ dbc.Card(
                [
                    dbc.CardHeader("Mission Milestone Dates", style = {'textAlign' : 'center'}),
                    dbc.CardBody(
                        [dcc.Markdown(id='milestone_description', children=[], style = {'textAlign' : 'center'}), #e1e5ea
                        ]
                    ),
                ]
            )
            ]), width = 3)

col_rad = dbc.Col(html.Div(id = 'rad_table'), width = 4)

colMission = html.Div([
    # Flex container
    html.Div([

        # Graph container
        html.Div(id = 'summary_table', style={'width': '45%', 'display': 'inline-block'}),

        # Table container
        html.Div([
            dbc.Card(
                [
                    dbc.CardHeader("Mission Milestone Dates", style = {'textAlign' : 'center'}),
                    dbc.CardBody(
                        [dcc.Markdown(id='milestone_description', children=[], style = {'textAlign' : 'center'}), #e1e5ea
                        ]
                    ),
                ]
            )
        ], style={'width': '49%', 'display': 'inline-block'}),

    ], style={'display': 'flex'}),

])


app.layout = html.Div([
    dbc.Row([col]),
    html.H4(children='Summary of Environmental and Radiation Data'),
    #dbc.Row([col_summary, colMission]),
    dbc.Row([colMission]),
    html.Br(),
    html.H4(children='Environmental Data'),
    dbc.Row(col_eda),
    html.Br(),
    html.H4(children='Radiation Data'),
    dbc.Row(col_rad),
])
