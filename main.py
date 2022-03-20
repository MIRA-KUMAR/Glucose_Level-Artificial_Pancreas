# Importing libraries

import pandas as pd
import datetime as dt
pd.options.mode.chained_assignment = None

raw_cgm_data = pd.read_csv('CGMData.csv', low_memory=False)

# Getting only necessary columns

req_cgm_data = raw_cgm_data[['Date', 'Time', 'Sensor Glucose (mg/dL)']].copy()
req_cgm_data['Timestamp'] = pd.to_datetime(
    raw_cgm_data['Date'] + ' ' + raw_cgm_data['Time'])

# Missing values in CGM data:

sensor_data = req_cgm_data['Sensor Glucose (mg/dL)']
no_of_missing_data = sensor_data.isnull().sum()
percent_missing = (no_of_missing_data/len(sensor_data))*100

# Analyzing Insulin Data

raw_insulin_data = pd.read_csv('InsulinData.csv', low_memory=False)

# Getting only necessary columns

req_insulin_data = raw_insulin_data[['Date', 'Time', 'Alarm']]
req_insulin_data['Timestamp'] = pd.to_datetime(
    raw_insulin_data['Date'] + ' ' + raw_insulin_data['Time'])

# Checking Auto Mode => 'AUTO MODE ACTIVE PLGM OFF'

auto_mode_rows = req_insulin_data[req_insulin_data['Alarm']
                                  == 'AUTO MODE ACTIVE PLGM OFF']

# Getting timestamp from Insulin data at which Automode starts:

auto_mode_timestamp = auto_mode_rows.iloc[-1]['Timestamp']

# Getting auto_mode timestamp from CGM Data at which Automode starts:

cgm_auto_mode_timestamp = req_cgm_data[req_cgm_data['Timestamp']
                                       >= auto_mode_timestamp].iloc[-1]['Timestamp']

# Dividing into auto mode and manual mode :

cgm_data_auto_mode = req_cgm_data[req_cgm_data['Timestamp']
                                  >= cgm_auto_mode_timestamp]
cgm_data_manual_mode = req_cgm_data[req_cgm_data['Timestamp']
                                    < cgm_auto_mode_timestamp]

# Converting to DateTime:

for column in ['Date', 'Time']:
    cgm_data_auto_mode.loc[column] = pd.to_datetime(cgm_data_auto_mode[column])
    cgm_data_manual_mode.loc[column] = pd.to_datetime(
        cgm_data_manual_mode[column])

# Splitting auto mode dataset for datetime and overnight shifts:

cgm_data_auto_mode_daytime = cgm_data_auto_mode[cgm_data_auto_mode['Timestamp'].dt.time >= dt.time(
    6, 0, 0)].copy()
cgm_data_auto_mode_overnight = cgm_data_auto_mode[cgm_data_auto_mode['Timestamp'].dt.time < dt.time(
    6, 0, 0)].copy()

# Splitting Manual mode dataset for datetime and overnight shifts:

cgm_data_manual_mode_daytime = cgm_data_manual_mode[cgm_data_manual_mode['Timestamp'].dt.time >= dt.time(
    6, 0, 0)].copy()
cgm_data_manual_mode_overnight = cgm_data_manual_mode[cgm_data_manual_mode['Timestamp'].dt.time < dt.time(
    6, 0, 0)].copy()


# Results columns needed:

results = pd.DataFrame(columns=['Overnight Percentage time in hyperglycemia (CGM > 180 mg/dL)', 'Overnight percentage of time in hyperglycemia critical (CGM > 250 mg/dL)', 'Overnight percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL)', 'Overnight percentage time in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL)', 'Overnight percentage time in hypoglycemia level 1 (CGM < 70 mg/dL)', 'Overnight percentage time in hypoglycemia level 2 (CGM < 54 mg/dL)', 'Daytime Percentage time in hyperglycemia (CGM > 180 mg/dL)', 'Daytime percentage of time in hyperglycemia critical (CGM > 250 mg/dL)', 'Daytime percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL)',
                       'Daytime percentage time in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL)', 'Daytime percentage time in hypoglycemia level 1 (CGM < 70 mg/dL)', 'Daytime percentage time in hypoglycemia level 2 (CGM < 54 mg/dL)', 'Whole Day Percentage time in hyperglycemia (CGM > 180 mg/dL)', 'Whole day percentage of time in hyperglycemia critical (CGM > 250 mg/dL)', 'Whole day percentage time in range (CGM >= 70 mg/dL and CGM <= 180 mg/dL)', 'Whole day percentage time in range secondary (CGM >= 70 mg/dL and CGM <= 150 mg/dL)', 'Whole day percentage time in hypoglycemia level 1 (CGM < 70 mg/dL)', 'Whole Day percentage time in hypoglycemia level 2 (CGM < 54 mg/dL)'])

# To loop in the datasets:

datasets = [cgm_data_manual_mode_overnight, cgm_data_manual_mode_daytime, cgm_data_manual_mode,
            cgm_data_auto_mode_overnight, cgm_data_auto_mode_daytime, cgm_data_auto_mode]

# Function to calculate Percentage Time


def cal_mean_percentage_time(data, number_of_days):
    total = data.groupby(by='Date')['Time'].count()
    if len(total) == 0:
        return 0.0
    temp = (total/288)*100

    return temp.sum()/number_of_days


temp = []
for ind, data in enumerate(datasets):
    number_of_days = data['Date'].nunique()

    # 1. For hyperglycemia,
    hyperglycemia = cal_mean_percentage_time(
        data[data['Sensor Glucose (mg/dL)'] > 180], number_of_days)

    # 2. For hyperglycemia critical,
    hyperglycemia_critical = cal_mean_percentage_time(
        data[data['Sensor Glucose (mg/dL)'] > 250], number_of_days)

    # 3. For 'in range'
    in_range = cal_mean_percentage_time(data[(data['Sensor Glucose (mg/dL)'] >= 70) &
                                             (data['Sensor Glucose (mg/dL)'] <= 180)], number_of_days)

    # 4. For 'in range secondary'
    in_range_sd = cal_mean_percentage_time(data[(data['Sensor Glucose (mg/dL)'] >= 70) &
                                                (data['Sensor Glucose (mg/dL)'] <= 150)], number_of_days)

    # 5. For hypoglycemia level 1
    hyperglycemia_l1 = cal_mean_percentage_time(
        data[data['Sensor Glucose (mg/dL)'] < 70], number_of_days)

    # 6. For hypoglycemia level 2
    hyperglycemia_l2 = cal_mean_percentage_time(
        data[data['Sensor Glucose (mg/dL)'] < 54], number_of_days)

    temp.extend([hyperglycemia, hyperglycemia_critical, in_range,
                in_range_sd, hyperglycemia_l1, hyperglycemia_l2])

    if ind == 2:
        results.loc['Manual Mode'] = temp
        temp = []
    elif ind == 5:
        results.loc['Auto Mode'] = temp


results.to_csv('Results.csv', header=False, index=False)

# Done!

print('Done!')
