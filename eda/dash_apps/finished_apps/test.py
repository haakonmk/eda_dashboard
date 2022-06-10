
import pandas as pd

path = "/Users/hakonkolsto/Documents/django/djangoProject/eda/polls/input_files/"
mission_slctd = 'Rodent Research 1 (SpaceX-4)'
mission_info = pd.read_csv(path + "mission_info.csv")
mission_slctd = 'Rodent Research 1 (SpaceX-4)'
mission = mission_info[mission_info['Title'] == mission_slctd]['Mission']
try:
    df_eda = pd.read_json(path + '{}_CSV.json'.format(mission.item()))
except ValueError:
    print("Could not open/read file")



df_eda_init = pd.read_json(path + '{}_CSV.json'.format(mission.item()))
df_rad_init = pd.read_json(path + '{}_Radiation_CSV.json'.format(mission.item()))


def load_data(radiation = False):
    try:
        if radiation:
            df = pd.read_json(path + 'RR4_Radiation_CSV.json')
        else:
            df = pd.read_json(path + 'RR4_CSV.json')
        return df, ""
    except ValueError:
        if radiation:
            df = df_rad_init.copy()
        else:
            df = df_eda_init.copy()
        for col in df.columns:
            df[col].values[:] = 0
        return df, "Data not available."


df_eda, data_status_eda = load_data()
df_rad, data_status_rad = load_data(True)
print("df_rad: {}".format(df_rad.head()))
print("df_eda: {}".format(df_eda.head()))
df_eda.Controller_Time_GMT = pd.to_datetime(df_eda.Controller_Time_GMT)
df_rad['Accumulated_Radiation'] = df_rad['Total_Dose_mGy_d'].cumsum()
