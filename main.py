import os

from flask import Flask, redirect, url_for, render_template, jsonify, request
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform

import matplotlib.pyplot as plt 
from sklearn.manifold import MDS
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np
import json, math
import geojson
import random

## Flask variables
app = Flask(__name__)
app.secret_key = "hello"

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

## global Variables
curr_dir = os.path.dirname(__file__)

# data paths
data_path = os.path.join(curr_dir, os.path.join('data', "owid-covid-data.csv"))
# geo_json_path = os.path.join(curr_dir, os.path.join('data', 'countries.geo.json'))
geo_json_path = os.path.join(curr_dir, os.path.join('data', 'countries_with_crop.json'))
# covid_geo_json_path = os.path.join(curr_dir, os.path.join('data', 'covid_geo.json'))
covid_geo_json_path = os.path.join(curr_dir, os.path.join('data', 'countries_with_crop.json'))

world_line_data_path = os.path.join(curr_dir, os.path.join('data', "world-data.csv"))
bubble_data_path = os.path.join(curr_dir, os.path.join('data', "bubble_npi.csv"))
barchart_data_path = os.path.join(curr_dir, os.path.join('data', "world-seasonal-data.csv"))
hashtags_data_path = os.path.join(curr_dir, os.path.join('data', "hashtags.csv"))

agri_data_path = os.path.join(curr_dir, os.path.join('data', "reduced_data_new.xlsx"))

with open(geo_json_path) as f:
    gj = geojson.load(f)
    for i in range(len(gj["features"])):
        if(gj["features"][i]["properties"]["name"] == "Antarctica"):
            gj["features"].remove(gj["features"][i])
            break

# Geo features for plotting world map
geo_features = gj['features']

# read data
data = pd.read_csv(data_path)
data_original = data.copy()

pcp_data = pd.DataFrame()

bar_df = pd.read_csv(barchart_data_path)
world_line_df = pd.read_csv(world_line_data_path)
bubble_df = pd.read_csv(bubble_data_path)
hashtag_df = pd.read_csv(hashtags_data_path)

agri_df = pd.read_excel(agri_data_path)
top_10 = dict()
bottom_10 = dict()

country_avg_df = None
df_mds_corr = None
time_series_df = None

selected_attributes = ['crop_production_index', 'food_production_index', 'GDP_per_capita', 'agricultural_machinery_tractors_100_sqkm', 'Access_to_electricity_rural_percent', 'agricultural_land_percent', 'Rural_population_percent', 'Agricultural_raw_materials_imports_percent', 'Agricultural_raw_materials_exports_percent', 'Arable_land_percent']
selected_attributes_dict = {'crop_production_index': 1, 'food_production_index': 1, 'GDP_per_capita': 0.004, 'agricultural_machinery_tractors_100_sqkm': 0.1, 'Access_to_electricity_rural_percent': 1, 'agricultural_land_percent': 1, 'Rural_population_percent': 1, 'Agricultural_raw_materials_imports_percent': 10, 'Agricultural_raw_materials_exports_percent': 10, 'Arable_land_percent': 1}

def normalise2():
    global agri_df
    global selected_attributes_dict
    global time_series_df

    time_series_df = agri_df.copy(deep = True)
    for col in selected_attributes_dict:
        print('column focused: ', col)
        time_series_df['normalised_' + col] = agri_df[col] * selected_attributes_dict[col]
    
    # print('time_series: ', time_series_df)





    # # make a copy of dataframe
    # scaled_features = agri_df.drop(['Country_Name', 'Country_Code'], axis=1 )

    # features = scaled_features[selected_attributes]

    # # Use scaler of choice; here Standard scaler is used
    # scaler = StandardScaler().fit(features.values)
    # features = scaler.transform(features.values)

    # scaled_features[selected_attributes] = features
    # print(scaled_features[selected_attributes])



def normalise():
    global agri_df
    df_kept = agri_df.drop(['Country_Name', 'Country_Code'], axis=1 )
    normalised_df = (df_kept - df_kept.min()) / (df_kept.max() - df_kept.min()) * 100
    # print('Normalised df: ', normalised_df)
    # agri_df.merge(normalised_df.rename(columns=lambda x: {x: 'normalised ' + x}), left_index=True, right_index=True )
    # df.toDF(*newColumns)
    columns = normalised_df.columns
    new_columns = ['normalised_' + column for column in columns]
    # print('columns: ', columns)
    # print('new_columns: ', new_columns)
    normalised_df.columns = new_columns
    # print('normalised_df: ', normalised_df)
    time_series_df = pd.concat([agri_df, normalised_df], axis=1, join='inner')
    # print('final_df: ', agri_df)

    




def compute_average():
    global agri_df
    global country_avg_df
    country_avg_df = agri_df.groupby('Country_Name', as_index=False).mean()
    print('Country average df: ', country_avg_df)


def sort_countries(field_name):
    global country_avg_df
    # print(field_name)
    # temp_df = agri_df.copy(deep = True)

    filtered_df = country_avg_df.filter(['Country_Name', field_name])
    sorted_df = filtered_df.sort_values(field_name, ascending=False)
    # print('------------------ sorted df --------------')
    # print(sorted_df)

    top = sorted_df.head(10)
    bottom = sorted_df.tail(10)
    # print('bottom: ', bottom)
    # print('top: ', top)
    return top, bottom

@app.route("/agriBarData", methods=["POST" , "GET"])
def agriBarData():
    global top_10
    global bottom_10

    if(request.method == 'POST'):
        reqbody = request.get_json()
        field = reqbody["attribute"]
    
    top10ForField = top_10[field]
    top10ForField.rename(columns = {'Country_Name':'country', field:'value'}, inplace = True)
    jsonStr = json.dumps(top10ForField.to_dict(orient="records"))
    return jsonStr



def compute_10():
    global bottom_10
    global top_10
    for field_name in agri_df.columns[4:]:
        top, bottom = sort_countries(field_name)
        bottom_10[field_name] = bottom
        top_10[field_name] = top

    
    

def preprocess():
    global data
    data.fillna(0, inplace=True)
    data = data[~data['iso_code'].astype(str).str.startswith('OWID')]
    data.reset_index(drop=True, inplace=True)
    data.rename({"iso_code" : "id"}, axis="columns", inplace=True)
    data['date'] = pd.to_datetime(data['date'])
    
    countries = []
    
    for i in range(len(gj["features"])):
        id = gj["features"][i]["id"]
        if(id in data["id"].values):
            countries.append(id)
            
    data = data.loc[data.id.isin(countries)].reset_index(drop=True)
    

def preprocess_pcp_data():
    global data
    global pcp_data
    
    pcp_data=data
    ## countries in npi data

    # countries = ['ALB', 'AUT', 'BEL', 'BIH', 'BRA', 'CAN', 'HKG', 'HRV', 'CZE',
    #    'DNK', 'ECU', 'EGY', 'SLV', 'EST', 'FIN', 'FRA', 'DEU', 'GHA',
    #    'GRC', 'HND', 'HUN', 'ISL', 'IND', 'IDN', 'ITA', 'JPN', 'KAZ',
    #    'RKS', 'KWT', 'LIE', 'LTU', 'MYS', 'MUS', 'MEX', 'MNE', 'NLD',
    #    'NZL', 'MKD', 'NOR', 'POL', 'PRT', 'IRL', 'ROU', 'SEN', 'SRB',
    #    'SGP', 'SVK', 'SVN', 'KOR', 'ESP', 'SWE', 'CHE', 'SYR', 'TWN',
    #    'THA', 'GBR', 'USA', 'AUS']

    countries = ['ARG', 'AUT', 'AZE', 'BHS', 'BGD', 'BLR', 'BEL', 'BEN', 'BOL',
     'BWA', 'BRA', 'BGR', 'BFA', 'CPV', 'KHM', 'CAN', 'CHL', 'CHN',
     'COL', 'CIV', 'HRV', 'CUB', 'CYP', 'CZE', 'DNK', 'ECU', 'EGY',
     'ERI', 'EST', 'SWZ', 'FJI', 'FIN', 'FRA', 'DEU', 'GHA', 'GRC',
     'HND', 'HUN', 'IND', 'IDN', 'IRN', 'IRL', 'ISR', 'ITA', 'JPN',
     'JOR', 'KAZ', 'KEN', 'KOR', 'KWT', 'KGZ', 'LVA', 'LTU', 'LUX',
     'MDG', 'MLI', 'MLT', 'MRT', 'MEX', 'MDA', 'MNG', 'MAR', 'NPL',
     'NLD', 'NIC', 'NER', 'NGA', 'MKD', 'NOR', 'OMN', 'PAK', 'PAN',
     'PRY', 'PER', 'PHL', 'POL', 'PRT', 'QAT', 'ROU', 'RUS', 'SAU',
     'SEN', 'SVK', 'SVN', 'ZAF', 'ESP', 'VCT', 'SUR', 'SWE', 'CHE',
     'TJK', 'TZA', 'THA', 'TGO', 'TTO', 'TUN', 'UKR', 'ARE', 'USA',
     'URY', 'VNM', 'YEM', 'ZWE']
    
    # to_remove = ["SEN", "SLV", "BIH", "TWN", "BEL", "HRV", "SYR", "MNE", "CZE", "MKD", "SVK", "GHA", "EGY", "EST", "ROU"]

    pcp_data = data.loc[data.id.isin(countries)].reset_index(drop=True)
    # pcp_data = pcp_data.loc[~pcp_data.id.isin(to_remove)].reset_index(drop=True)  
    


@app.route("/agrimds", methods=["POST" , "GET"])
def get_agri_mds():
    # df_country = pd.read_csv("/content/drive/MyDrive/CSE564 VIS/Cleaned_data.csv")
    global agri_df
    global df_mds_corr
    global country_avg_df
    mds_pc = MDS(n_components=2, dissimilarity='precomputed')
    df_kept = agri_df.drop(['Country_Name', 'Country_Code'], axis=1 )
    # mds_fitted_pc = mds_pc.fit(1- np.abs(df_kept.corr()))
    corr_mat = 1 - np.abs(df_kept.corr())
    mds_fitted_pc = mds_pc.fit(corr_mat)

    # print('----------------- Correlation Matrix ----------------: ', corr_mat)

    df_mds_corr = pd.DataFrame.from_records(mds_fitted_pc.embedding_, columns=['x','y'])
    df_mds_corr['fields'] = df_kept.columns
    res_corr_values = get_corr_values()
    # return {'points': json.dumps(df_mds_corr.to_dict(orient="records"), 'corr_values': res)}
    responseToSend = {}
    responseToSend["points"] = df_mds_corr.to_dict(orient="records")
    responseToSend["corr_values"] = res_corr_values
    return json.dumps(responseToSend)


def get_corr_values():
    global agri_df
    # mds_pc = MDS(n_components=2, dissimilarity='precomputed')
    # df_kept = agri_df.drop(['Country_Name', 'Country_Code'], axis=1 )
    # mds_fitted_pc = mds_pc.fit(1- np.abs(df_kept.corr()))
    # df_mds_corr = pd.DataFrame.from_records(mds_fitted_pc.embedding_, columns=['x','y'])
    # df_mds_corr['fields'] = df_kept.columns

    temp_df = country_avg_df.filter(items = selected_attributes)
    # print('temp_df: ', temp_df)
    # temp2_df = temp_df.drop(columns = 'fields')
    # print(temp_df)

    corr_matrix = temp_df.corr()

    corr_mat = corr_matrix.to_numpy()

    # print('--------------- corrMatrix ------------------:', corr_mat)

    # distance = pdist(temp2_df, 'cosine')
    # print('distance: ', distance)

    # # for i in range(len(distance)):
    # #     distance[i] = 1.0 - distance[i]

    # print('new distance: ', distance)
    # corr_matrix = 1 - squareform(distance)
    # print('corr_matrix: ', corr_matrix)

    res = []
    i, j = 0, 0
    for field in temp_df:
        for field2 in temp_df:
            if i > j:
                res.append({'field1': field, 'field2': field2, 'value': corr_mat[i][j]})
            j += 1
        i += 1
        j = 0
            

    # print(res)
    #pairwise = pd.Dataframe(corr_matrix, columns = df_mds_corr['fields'], index = df_mds_corr['fields'])
    #return json.dumps(pairwise.to_dict(orient = "records"))

    return res




@app.route("/agriPcp", methods=["POST" , "GET"])
def get_agri_pcp_data():
    global country_avg_df
    global agri_df
    
    if(request.method == 'POST'):
        dates = request.get_json()
    
    pcp_axis = [
    #    'index', 'Country_Name', 'Country_Code', 'year',
    #    'Access_to_electricity_percent',
       
        'GDP_per_capita',
       'agricultural_land_percent',
    #    'agricultural_land_sq_km',
    #    'agricultural_machinery_tractors',
    #    'agricultural_machinery_tractors_100_sqkm',
    #    'agricultural_methane_emissions_percent',
    #    '',
    #    'Agricultural_nitrous_oxide_emissions_percent',
    #    'Agricultural_nitrous_oxide_emissions',
       'Agricultural_raw_materials_exports_percent',
       'Agricultural_raw_materials_imports_percent',
    #    'Agriculture_forestry_fishing_value_in_gdp',
    #    'Agriculture_forestry_fishing_value_added_in_USD',
       'Arable_land_percent',
    #    'Arable_land',
    #    'Arable_land_hectares',
    #    'Birth_rate',
    #    'Cereal_production',
    #    'Cereal_yield',
       'crop_production_index',
    #    'Death_rate',
    #    'Employment_in_agriculture_percent',
    #    'Employment_in_agriculture_female',
    #    'Employment_in_agriculture_male',
       'food_production_index',
    #    'Forest_area_percent', 'Forest_area',
    'Access_to_electricity_rural_percent',
    #    'Land_area',
    #    'Land_under_cereal_production ',
       'Livestock_production_index',
    #    'Mineral_rents_percent',
    #    'Mortality_rate',
       'Permanent_cropland_percent',
    #    'Population_total',
    #    'Rural_population', 'Rural_population_percent',
       'Rural_population_growth_percent',
    #    'Surface_area'
    ]

    # pcp_data_temp = pcp_data_send[pcp_axis].groupby("location")[pcp_axis[2:]].mean().reset_index()
    # pcp_data_temp["id"] = pcp_data_send["id"].unique()
        
    # return json.dumps(pcp_data_temp.to_dict(orient="records"))
    dataToReturn = {}
    dataToReturn["order"] = pcp_axis
    
    # temp_df = country_avg_df.filter(items = selected_attributes)
    # temp_df['cluster'] = KMeans(n_clusters=2).fit(temp_df).labels_

    # country_avg_df['cluster'] = KMeans(n_clusters=3).fit(country_avg_df[['GDP_per_capita']]).labels_
    # country_avg_df['cluster'] = KMeans(n_clusters=3).fit(country_avg_df[['GDP_per_capita']]).labels_
    country_avg_df['cluster'] = KMeans(n_clusters=3).fit(country_avg_df[['crop_production_index']]).labels_
    dataToReturn["pcpData"] = country_avg_df.to_dict(orient="records")


    # print('--------------------- temp_df -------------------: ', temp_df)
    # number = country_avg_df.shape[0]
    # cluster1 = temp_df[temp_df["clusters"] == 0].sample(number // 2, replace = True)
    # cluster2 = temp_df[temp_df["clusters"] == 1].sample(number - (number // 2), replace = True)
    # data = pd.DataFrame([], columns=pcp_axis)
    # data = pd.concat([data, cluster1], ignore_index=True)
    # data = pd.concat([data, cluster2], ignore_index=True)

    # print('--------------------- data -------------------: ', data)
    # output = pd.DataFrame(np.append(MDS(n_components=2,dissimilarity="euclidean").fit_transform(StandardScaler().fit_transform(data.drop(["clusters"],axis=1))), data['clusters'].values.reshape(math.ceil(data.shape[0]), 1), axis=1),columns=pcp_axis)
    

    # print('---------------------- output --------------:', output)
    # dataToReturn["pcpData"] = output.to_dict(orient = "records")

    return json.dumps(dataToReturn)


@app.route("/worldmap", methods=["POST" , "GET"])
def get_worldmap_data():
    
    start_date = pd.to_datetime("2019-03-25")
    end_date = pd.to_datetime("2022-03-28")
    
    if(request.method == 'POST'):
        dates = request.get_json()

        start_date = pd.to_datetime(dates["start"])
        end_date = pd.to_datetime(dates["end"])
                    
    filtered_data = data.loc[(data.date>=start_date) & (data.date<=end_date)]
    
    groupby_data = filtered_data.groupby(["id"])
    
    mean_new_cases = groupby_data.new_cases.mean()
    mean_new_deaths = groupby_data.new_deaths.mean()
    mean_new_vaccinations = groupby_data.new_vaccinations.mean()
        
    for i in range(len(gj["features"])):
        id = gj["features"][i]["id"]
        if(id in filtered_data["id"].values):
            gj["features"][i]["new_cases"] = int(mean_new_cases[id])
            gj["features"][i]["new_deaths"] = int(mean_new_deaths[id])
            gj["features"][i]["new_vaccinations"] = int(mean_new_vaccinations[id])  

    return gj


@app.route("/agriLineChart", methods=["GET","POST"])
def get_agri_linechart_data():
    global time_series_df

    country = "USA"
    if(request.method == 'POST'):
        reqbody = request.get_json()
        country = reqbody["country"]
        # print(country)

    if country != "world":
        # print("is it going here???")
        agri_line_df = time_series_df.loc[agri_df["Country_Code"]==country]
    else:
        agri_line_df = time_series_df.loc[agri_df["Country_Code"]=="USA"]
    d1 = agri_line_df.to_dict(orient="records")
    D = { "agriLineData":d1 }
    return json.dumps(D)

# @app.route("/agrimds")
# def get_agri_mds():
#     global agri_df
#     mds_pc = MDS(n_components=2, dissimilarity='precomputed')
#     df_kept = agri_df.drop(['Country_Name', 'Country_Code'], axis=1 )
#     mds_fitted_pc = mds_pc.fit(1- np.abs(df_kept.corr()))
#     df_mds_corr = pd.DataFrame.from_records(mds_fitted_pc.embedding_, columns=['x','y'])
#     df_mds_corr['fields'] = df_kept.columns
#     return json.dumps(df_mds_corr.to_dict(orient="records"))


@app.route("/")
def home():
    return render_template("index.html")


if(__name__ == "__main__"):
    normalise2()
    compute_average()
    preprocess()
    preprocess_pcp_data()
    compute_10()
    # get_corr_values()

    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True, port=4001)




#############################################################################################################

'''
@app.route("/pcp", methods=["POST" , "GET"])
def get_pcp_data():
    global pcp_data
    
    start_date = pd.to_datetime("2019-01-01")
    end_date = pd.to_datetime("2022-11-23")
    
    if(request.method == 'POST'):
        dates = request.get_json()

        start_date = pd.to_datetime(dates["start"])
        end_date = pd.to_datetime(dates["end"])

    pcp_data_send = pcp_data.loc[(pcp_data.date>=start_date) & (pcp_data.date<=end_date)]
    
    # pcp_axis = ["id","location", 'gdp_per_capita', 'stringency_index', 'human_development_index', 'median_age', 'hospital_beds_per_thousand', 'positive_rate', 'new_cases_per_million', 'new_deaths_per_million', 'new_vaccinations_smoothed_per_million']
    pcp_axis = [
       'index', 'Country_Name', 'Country_Code', 'year',
       'Access_to_electricity_percent',
       'Access_to_electricity_rural_percent',
       'agricultural_land_percent', 'agricultural_land_sq_km',
       'agricultural_machinery_tractors',
       'agricultural_machinery_tractors_100_sqkm',
       'agricultural_methane_emissions_percent',
       'Agricultural_methane_emissions',
       'Agricultural_nitrous_oxide_emissions_percent',
       'Agricultural_nitrous_oxide_emissions',
       'Agricultural_raw_materials_exports_percent',
       'Agricultural_raw_materials_imports_percent',
       'Agriculture_forestry_fishing_value_in_gdp',
       'Agriculture_forestry_fishing_value_added_in_USD',
       'Arable_land_percent', 'Arable_land',
       'Arable_land_hectares', 'Birth_rate',
       'Cereal_production', 'Cereal_yield',
       'crop_production_index',
       'Death_rate',
       'Employment_in_agriculture_percent',
       'Employment_in_agriculture_female',
       'Employment_in_agriculture_male',
       'food_production_index',
       'Forest_area_percent', 'Forest_area',
       'GDP_per_capita', 'Land_area',
       'Land_under_cereal_production ',
       'Livestock_production_index',
       'Mineral_rents_percent',
       'Mortality_rate',
       'Permanent_cropland_percent', 'Population_total',
       'Rural_population', 'Rural_population_percent',
       'Rural_population_growth_percent', 'Surface_area'
    ]

    pcp_data_temp = pcp_data_send[pcp_axis].groupby("location")[pcp_axis[2:]].mean().reset_index()
    pcp_data_temp["id"] = pcp_data_send["id"].unique()
        
    return json.dumps(pcp_data_temp.to_dict(orient="records"))


@app.route("/linechart", methods=["POST" , "GET"])
def get_linechart_data():
    global world_line_df
    global bubble_df
    
    line_df = pd.DataFrame()
    npi_data = pd.DataFrame()
    
    country = "world"
    
    if(request.method == 'POST'):
        country = request.get_json()

    if(country == "world" or country==""):        
        line_df = world_line_df
    else:
        line_df = data.loc[data.id == country, ["date", "new_cases_smoothed", "new_deaths_smoothed", "new_vaccinations_smoothed"]]
        line_df.date = line_df.date.astype("str")
        line_df.rename(columns={'new_cases_smoothed': 'new_cases', 'new_deaths_smoothed': 'new_deaths', "new_vaccinations_smoothed" : "new_vaccinations"}, inplace=True)
        
    if(country != "world"):
        npi_data = bubble_df.loc[bubble_df['id']==country]
    else:
        npi_data = bubble_df
    
    if(npi_data.shape[0] != 0):
        npi_data['Date'] = pd.to_datetime(npi_data.Date)
    
        npi_data =  npi_data.groupby('Date')['Measure_L1'].value_counts().reset_index(name="Count") 
    
        npi_data['Count'] = npi_data['Count'].astype('int32')
        npi_data['Date'] = npi_data['Date'].astype('str')
        npi_data['Measure_L1'] = npi_data['Measure_L1'].str.replace('\s+', '_') 
        npi_data['Measure_L1'] = npi_data['Measure_L1'].str.replace(',', '')
        npi_data.rename(columns={'Date':'date'},inplace=True)

    d1 = line_df.to_dict(orient="records")
    d2 = npi_data.to_dict(orient="records")
    D = {'lined':d1,'bubbled':d2}
    return json.dumps(D)

@app.route("/stats", methods=["POST" , "GET"])
def get_stats_data():
    global world_line_df
    
    stats_line_df = pd.DataFrame()
    
    country = "world"
    
    start_date = pd.to_datetime("2019-03-25")
    end_date = pd.to_datetime("2022-03-28")
    
    if(request.method == 'POST'):
        finalVal = request.get_json()
        country = finalVal['country']
        dates = finalVal['date']
        if(dates["start"]!=""):
            start_date = pd.to_datetime(dates["start"])
            end_date = pd.to_datetime(dates["end"])

    if(country == "world"):        
        stats_line_df = world_line_df.copy()
        stats_line_df['date'] = pd.to_datetime(stats_line_df['date'])
        line_df_send = stats_line_df.loc[(stats_line_df.date>=start_date) & (stats_line_df.date<=end_date)]
        line_df_send.drop(["date"], axis=1,inplace=True)
    else:
        stats_line_df = data.loc[data.id == country, ["date", "new_cases_smoothed", "new_deaths_smoothed", "new_vaccinations_smoothed"]]
        stats_line_df['date'] = pd.to_datetime(stats_line_df['date'])
        line_df_send = stats_line_df.loc[(stats_line_df.date>=start_date) & (stats_line_df.date<=end_date)]
        line_df_send.drop(["date"], axis=1,inplace=True)
        line_df_send.rename(columns={'new_cases_smoothed': 'new_cases', 'new_deaths_smoothed': 'new_deaths', "new_vaccinations_smoothed" : "new_vaccinations"}, inplace=True)
    
    return json.dumps(line_df_send.to_dict(orient="records"))

@app.route("/barchart", methods=["POST" , "GET"])
def get_barchart_data():
    global bar_df
    
    return json.dumps(bar_df.to_dict(orient="records"))

@app.route("/wordcloud", methods=["POST" , "GET"])
def get_wordcloud_data():
    global hashtag_df
    
    start_date = pd.to_datetime("2019-01-15")
    end_date = pd.to_datetime("2022-01-30")

    
    if(request.method == 'POST'):
        dates = request.get_json()
        start_date = pd.to_datetime(dates["start"])
        end_date = pd.to_datetime(dates["end"])
    
    
    hashtag_df['date'] = pd.to_datetime(hashtag_df['date'])
    
    date_check = np.where((hashtag_df.date>=start_date) & (hashtag_df.date<=end_date))
    
    word_cloud_df = hashtag_df.loc[date_check]
        
    word_cloud_df = word_cloud_df.groupby(["hashtag"])['count'].sum().astype('int64').sort_values().tail(20).reset_index()
    word_cloud_df['count'] = np.log(word_cloud_df['count'])
    
    return json.dumps(word_cloud_df.to_dict(orient="records"))
'''