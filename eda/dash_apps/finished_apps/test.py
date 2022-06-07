
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



def load_data(mission, radiation = False):
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
