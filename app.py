import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import pandas as pd
import zipfile
from PIL import Image


st.set_page_config(layout="wide")



#--------------------------Lectura datos de temperatura---------------------------------------
rutaT = 'https://raw.githubusercontent.com/IngButters/ClimaData/master/est_sup_temp_fase_2.csv'

ruta_ub = 'https://raw.githubusercontent.com/IngButters/ClimaData/master/Ubicacion_puntos.csv'

#--------------------------Lectura datos de precipitación-------------------------------------
rutaP = 'https://raw.githubusercontent.com/IngButters/ClimaData/master/est_sup_precip_fase_2.csv'





df_radiacion = pd.read_csv('https://raw.githubusercontent.com/IngButters/ClimaData/master/radiacion.csv')
df_radiacion.rename(columns={'Latitud': 'latitud'}, inplace=True)
#df_radiacion

def calcEvapotranspiracion(df_tempSup, df_ub, df_radiacion,tempGet):
    """     
    Returns the dataframe of the evapotranspiration calculated with Turc Modified

            Parameters:
                    df_tempSup (Dataframe): A pandas dataframe with temperature data
                    df_ub (Dataframe): A pandas dataframe with the location of the stations
                    df_radiacion (Dataframe): A pandas dataframe with the location of the stations
                    tempGet (list): List of the temperature stations selected

            Returns:
                    df_tempSup (Dataframe): Dataframe of the evapotranspiration calculated
    """

    df_new = pd.DataFrame()
    HR = [82.065943, 82.91073, 85.125509, 85.536313, 85.341042, 83.060406, 80.410283, 78.7061, 79.407464, 83.32468, 85.336647, 84.15651]
    meses = ['Ene',	'Feb',	'Mar',	'Abr',	'May',	'Jun',	'Jul',	'Ago',	'Sep',	'Oct',	'Nov',	'Dic']
    K = [0.4, 0.37, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4]
    N = [31,28,31,30,31,30,31,31,30,31,30,31]

    #df_tempSup.rename(columns={'fecha': 'date'}, inplace=True)
    df_tempSup['date'] = pd.date_range(start='01/01/1950', periods=len(df_tempSup), freq='D')
    df_tempSup.set_index('date', inplace=True)

    for i in df_tempSup.columns:
        df_new = df_new.append(df_ub.loc[df_ub.index == int(i)])

    df_radiacion = pd.concat([df_radiacion,df_new[['latitud']]],ignore_index = False).sort_values(['latitud'], ascending=True)
    df_radiacion = df_radiacion.interpolate()

    df_evapot = pd.merge(df_new, df_radiacion, left_index=True, right_index=True)

    
    for n, j, i, in zip(range(1,13), K, HR):
        df_tempSup[df_tempSup.index.month.isin([n])] = (j * ((df_tempSup[df_tempSup.index.month.isin([n])])/((df_tempSup[df_tempSup.index.month.isin([n])])+15))) * (1+((50-i)/70))

    for m in meses:
        df_evapot[[str(m)]] = (df_evapot[[str(m)]]+50)

    for l in tempGet:
        for n, m, p in zip(range(1,13),meses,N):
            
            
            df_tempSup[l][df_tempSup.index.month.isin([n])] = (df_tempSup[l][df_tempSup.index.month.isin([n])] * df_evapot.loc[df_evapot.index == int(l), m].squeeze())
            df_tempSup[l][df_tempSup.index.month.isin([n])] = ((df_tempSup[l][df_tempSup.index.month.isin([n])])/p)
            

    df_tempSup = df_tempSup.fillna(-1)
    df_tempSup.reset_index(inplace=True)
    del df_tempSup['date']
    return df_tempSup


def abrirArchivos(ruta, letra, columnas):
    """ 
    Returns the dataframe of the data opened

            Parameters:
                    ruta (String): A string with the location of the file
                    letra (String): A string with the identification of the data type -> P=Precipitation, T=Temperature

            Returns:
                    df_datos (Dataframe): Dataframe with the information of precipitation or temperature 

    """
    if letra == "P":
        df_datos = pd.read_csv(ruta, usecols = columnas)
        #df_datos = df_datos.fillna(-1)
        #df_datos.fecha = pd.to_datetime(df_datos.fecha)

    else:
        df_datos = pd.read_csv(ruta, usecols = columnas)
        #df_datos = df_datos.fillna(-99)
        #df_datos.fecha = pd.to_datetime(df_datos.fecha, usecols = columnas)

    return df_datos

#-----------------------------------Ubicacion estaciones precipitacion----------------------------------
def ubicacion_estaciones(ruta_ub):
    """     
    Returns the dataframe of the location of stations

            Parameters:
                    ruta_ub (String): A string with the location of the file

            Returns:
                    df_ubic (Dataframe): Dataframe with the information of the location of the stations
     """

    df_ubic = pd.read_csv(ruta_ub, usecols=['CODIGO','altitud','longitud','latitud'], encoding='latin-1')
    #df_ubic = df_ubic_precdf_ubicip_sup.round(decimals=2)

    return df_ubic


df_ub = ubicacion_estaciones(ruta_ub)
df_ub['CODIGO'] = df_ub['CODIGO'].astype(str)
df_ub2 = df_ub.set_index('CODIGO')
#df_ub

def download_zip_file(file_paths):
    with zipfile.ZipFile("download.zip", "w") as zip:
        for file in file_paths:
            zip.write(file)
    return


#------------------Trimestre Precipitacion---------------------------------
def trimestre_precip(df_precipSup, rcp_clima):
    """     
    Returns the the dataframe of the precipitation with climate change scenarios

            Parameters:
                    df_precip_sup (Dataframe): A pandas dataframe with precipitation data
                    rcp_clima (String): A string that for the climate change scenario selected

            Returns:
                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) (Dataframe, Dataframe, Dataframe): Dataframe with climate change scenario for timelapse of 2011-2040, 2041-2070, 2071-2100
     """

    df_precipSup['date'] = pd.date_range(start='01/01/1950', periods=len(df_precipSup), freq='D')
    df_precipSup.set_index(['date'], inplace=True)
    df_precipSup_2011_2040 = df_precipSup.copy(deep=True)
    df_precipSup_2041_2070 = df_precipSup.copy(deep=True)
    df_precipSup_2071_2100 = df_precipSup.copy(deep=True)

    if rcp_clima == '2.6':
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] * 0.9327
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] * 1.0751
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] * 1.0936
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] * 1.0786

        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] * 0.9577
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] * 1.1045
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] * 1.205
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] * 1.0476

        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] * 0.9461
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] * 1.089
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] * 1.1974
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] * 1.0336

    elif rcp_clima == '4.5':
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] * 0.9387
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] * 1.0205
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] * 1.1089
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] * 1.0943

        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] * 0.9668
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] * 0.995
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] * 1.1834
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] * 1.0442

        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] * 1.0003
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] * 1.0362
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] * 1.1974
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] * 1.0675

    elif rcp_clima == '6.0':
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] * 0.9389
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] * 1.0213
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] * 1.1054
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] * 1.1117

        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] * 0.9814
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] * 1.0586
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] * 1.1846
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] * 1.039

        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] * 1.0249
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] * 1.0707
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] * 1.2297
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] * 1.033

    elif rcp_clima == '8.5':
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([12,1,2])] * 0.9301
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([3,4,5])] * 1.0551
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([6,7,8])] * 1.1334
        df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] = df_precipSup_2011_2040[df_precipSup_2011_2040.index.month.isin([9,10,11])] * 1.1503

        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([12,1,2])] * 0.9776
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([3,4,5])] * 1.0996
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([6,7,8])] * 1.2304
        df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] = df_precipSup_2041_2070[df_precipSup_2041_2070.index.month.isin([9,10,11])] * 1.0842

        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([12,1,2])] * 1.0647
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([3,4,5])] * 1.1436
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([6,7,8])] * 1.2125
        df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] = df_precipSup_2071_2100[df_precipSup_2071_2100.index.month.isin([9,10,11])] * 0.9771

    df_precipSup_2011_2040.reset_index(inplace=True)
    df_precipSup_2041_2070.reset_index(inplace=True)
    df_precipSup_2071_2100.reset_index(inplace=True)
    
    del df_precipSup_2011_2040['date']
    del df_precipSup_2041_2070['date']
    del df_precipSup_2071_2100['date']

    return (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100)

#---------------------Trimestre Temperatura------------------------------------------------
def trimestre_temp(df_tempSup, rcp_clima):
    """     
    Returns the the dataframe of the temperature with climate change scenarios

            Parameters:
                    df_precip_sup (Dataframe): A pandas dataframe with precipitation data
                    rcp_clima (String): A string that for the climate change scenario selected

            Returns:
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) (Dataframe, Dataframe, Dataframe): Dataframe with climate change scenario for timelapse of 2011-2040, 2041-2070, 2071-2100
    """
    df_tempSup['date'] = pd.date_range(start='01/01/1950', periods=len(df_tempSup), freq='D')
    df_tempSup.set_index(['date'], inplace=True)
    df_tempSup_2011_2040 = df_tempSup.copy(deep=True)
    df_tempSup_2041_2070 = df_tempSup.copy(deep=True)
    df_tempSup_2071_2100 = df_tempSup.copy(deep=True)

    if rcp_clima == '2.5':
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] + 0.98
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] + 0.92
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] + 0.94
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] + 0.88

        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] + 1.32
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] + 1.3
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] + 1.31
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] + 1.21

        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] + 1.37
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] + 1.26
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] + 1.28
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] + 1.22

    elif rcp_clima == '4.5':
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] + 1.15
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] + 1.02
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] + 1.05
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] + 0.99

        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] + 1.88
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] + 1.82
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] + 1.81
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] + 1.70

        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] + 2.22
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] + 2.04
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] + 2.11
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] + 1.99

    elif rcp_clima == '6.0':
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] + 1.05
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] + 0.9
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] + 0.9
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] + 0.84

        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] + 1.69
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] + 1.62
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] + 1.65
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] + 1.53

        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] + 2.58
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] + 2.42
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] + 2.51
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] +2.32

    elif rcp_clima == '8.5':
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([12,1,2])] + 1.2
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([3,4,5])] + 1.07
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([6,7,8])] + 1.11
        df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] = df_tempSup_2011_2040[df_tempSup_2011_2040.index.month.isin([9,10,11])] + 1.04

        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([12,1,2])] + 2.47
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([3,4,5])] + 2.32
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([6,7,8])] + 2.38
        df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] = df_tempSup_2041_2070[df_tempSup_2041_2070.index.month.isin([9,10,11])] + 2.17

        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([12,1,2])] + 3.94
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([3,4,5])] + 3.67
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([6,7,8])] + 3.86
        df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] = df_tempSup_2071_2100[df_tempSup_2071_2100.index.month.isin([9,10,11])] + 3.55

    df_tempSup_2011_2040.reset_index(inplace=True)
    df_tempSup_2041_2070.reset_index(inplace=True)
    df_tempSup_2071_2100.reset_index(inplace=True)
    
    del df_tempSup_2011_2040['date']
    del df_tempSup_2041_2070['date']
    del df_tempSup_2071_2100['date']

    return (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100)


#--------------------------------Generar archivo de evento txt-----------------------------------------
def archivoEvento(df_precip_sup, df_tempSup, df_evapot, df_ubi_info, precpGet, tempGet, option5_evapot, nomb_archivo):
    """     
    Returns the column file format for Tetis software.

            Parameters:
                    df_precip_sup (Dataframe): A pandas dataframe with precipitation data
                    df_tempSup (Dataframe): A pandas dataframe with temperature data
                    df_evapot (Dataframe): A pandas dataframe with the evapotranspiration data
                    df_ubi_info (Dataframe): A pandas dataframe with the location of the stations
                    precpGet (list): List of the precipitation stations selected
                    tempGet (list): List of the temperature stations selected
                    option5_evapot (list): List of the evapotranspiration stations selected
                    nomb_archivo (string): String of the file name


            Returns:
                    Tetis_file (txt file): File in the column format for Tetis software
     """

    #Check if the user selected precipitation data
    if isinstance(df_precip_sup, pd.DataFrame):
        df_precip_sup_cond = df_precip_sup.loc[0].values[0]
    else:
        df_precip_sup_cond = df_precip_sup

    #Check if the user selected temperature data
    if isinstance(df_tempSup, pd.DataFrame):
        df_temp_sup_cond = df_tempSup.loc[0].values[0]
    else:
        df_temp_sup_cond = df_tempSup

    #Check if the user selected evapotranspiration data
    if isinstance(df_evapot, pd.DataFrame):
        df_evapot_cond = df_evapot.loc[0].values[0]
    else:
        df_evapot_cond = df_evapot

    


    #---------HEADER OF THE FILE-----------------------------------------------
    Tetis_file = open(nomb_archivo+".txt","w+")
    
    #Only temperature
    if (df_precip_sup_cond == 'None' and df_evapot_cond == 'None'):
                
        
        Tetis_file.write("G               "+str(len(df_tempSup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #Temperatura
        for j in tempGet:
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])   +'\n')

        #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = df_tempSup
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/2000  hasta:  31/12/2020\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))


    #Only precipitation
    elif (df_temp_sup_cond == 'None' and df_evapot_cond == 'None'):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])   +'\n')  

                #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = df_precip_sup
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/2000  hasta:  31/12/2020\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

    #Temperature and evapotranspiration
    elif (df_precip_sup_cond == 'None' and isinstance(df_tempSup, pd.DataFrame) and isinstance(df_evapot, pd.DataFrame)):
                
        
        Tetis_file.write("G               "+str(len(df_tempSup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #Temperatura1
        for j in tempGet:
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])   +'\n')

        for k in option5_evapot:
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])   +'\n')


        #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = pd.concat([df_tempSup,df_evapot], axis = 1)
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/2000  hasta:  31/12/2020\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

    #Precipitation and evapotranspiration
    elif (df_temp_sup_cond == 'None' and isinstance(df_precip_sup, pd.DataFrame) and isinstance(df_evapot, pd.DataFrame)):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])   +'\n')  

        for k in option5_evapot:
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])   +'\n')



                #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = pd.concat([df_precip_sup,df_evapot], axis = 1)
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/2000  hasta:  31/12/2020\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

    #Only evapotranspiration
    elif (df_temp_sup_cond == 'None' and df_precip_sup_cond == 'None'):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Evapotranspiration
        for k in option5_evapot:
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])   +'\n')



                #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = df_evapot
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/2000  hasta:  31/12/2020\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

    #Total---------------
    elif df_evapot_cond == 'None':
                #--------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-1950      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])   +'\n')  
        #Temperatura
        for j in tempGet:
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])   +'\n')
        
        #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = pd.concat([df_precip_sup, df_tempSup], axis = 1)
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/2000  hasta:  31/12/2020\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

    else:
        #--------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])   +'\n')  
        #Temperatura
        for j in tempGet:
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])   +'\n')
        #Evapotranspiration
        for k in option5_evapot:
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +'      '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])   +'\n')




        #-----------------------------INGRESAR LOS DATOS-------------------------------------------------------
        df_total = pd.concat([df_precip_sup, df_tempSup,df_evapot], axis = 1)
        df_total = df_total.round(decimals=2)
        Tetis_file.write("*dt(dia)\n")
        Tetis_file.write('* desde:  01/01/2000  hasta:  31/12/2020\n')
        Tetis_file.write('*')
        Tetis_file.write(df_total[df_total.columns].to_string(col_space=7))

    #Tetis_file.close()
    return Tetis_file

#-------------------------------------------------------Archivo CEDEX------------------------------------------------------------------------
def archivoCEDEX(df_precip_sup, df_tempSup, df_evapot, df_ubi_info, precpGet, tempGet, option5_evapot, nomb_archivo):

    """     
    Returns the CEDEX file format for Tetis software.

            Parameters:
                    df_precip_sup (Dataframe): A pandas dataframe with precipitation data
                    df_tempSup (Dataframe): A pandas dataframe with temperature data
                    df_evapot (Dataframe): A pandas dataframe with the evapotranspiration data
                    df_ubi_info (Dataframe): A pandas dataframe with the location of the stations
                    precpGet (list): List of the precipitation stations selected
                    tempGet (list): List of the temperature stations selected
                    option5_evapot (list): List of the evapotranspiration stations selected
                    nomb_archivo (string): String of the file name


            Returns:
                    Tetis_file (txt file): File in the CEDEX format for Tetis software
     """

    #Inciar condicion de precipitacion
    if isinstance(df_precip_sup, pd.DataFrame):
        df_precip_sup_cond = df_precip_sup.loc[0].values[0]
    else:
        df_precip_sup_cond = df_precip_sup

        #Inciar condicion de precipitacion
    if isinstance(df_tempSup, pd.DataFrame):
        df_temp_sup_cond = df_tempSup.loc[0].values[0]
    else:
        df_temp_sup_cond = df_tempSup

    #Check if the user selected evapotranspiration data
    if isinstance(df_evapot, pd.DataFrame):
        df_evapot_cond = df_evapot.loc[0].values[0]
    else:
        df_evapot_cond = df_evapot

    
    #---------HEADER-----------------------------------------------
    Tetis_file = open(nomb_archivo+".txt","w+")
    
    #Only temperature
    if (df_precip_sup_cond == 'None' and df_evapot_cond == 'None'):
                
        
        Tetis_file.write("G               "+str(len(df_tempSup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")


        for j in tempGet:
            arr_t = df_tempSup.T.loc[df_tempSup.T.index == j].to_numpy()
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')  



    #Only precipitation
    elif (df_temp_sup_cond == 'None' and df_evapot_cond == 'None'):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            arr_p = df_precip_sup.T.loc[df_precip_sup.T.index == i].to_numpy()
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_p))  +'\n')  


    #Temperature and evapotranspiration
    elif (df_precip_sup_cond == 'None' and isinstance(df_tempSup, pd.DataFrame) and isinstance(df_evapot, pd.DataFrame)):
                
        
        Tetis_file.write("G               "+str(len(df_tempSup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")


        for j in tempGet:
            arr_t = df_tempSup.T.loc[df_tempSup.T.index == j].to_numpy()
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')  

        for k in option5_evapot:
            arr_t = df_evapot.T.loc[df_evapot.T.index == k].to_numpy()
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')

    #Precipitation and evapotranspiration
    elif (df_temp_sup_cond == 'None' and isinstance(df_evapot, pd.DataFrame) and isinstance(df_precip_sup, pd.DataFrame)):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            arr_p = df_precip_sup.T.loc[df_precip_sup.T.index == i].to_numpy()
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_p))  +'\n')  

        for k in option5_evapot:
            arr_t = df_evapot.T.loc[df_evapot.T.index == k].to_numpy()
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')

    #Only evapotranspiration
    elif (df_temp_sup_cond == 'None' and df_precip_sup_cond == 'None'):
        #-------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Evapotranspiration
        for k in option5_evapot:
            arr_t = df_evapot.T.loc[df_evapot.T.index == k].to_numpy()
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')


    #Precipitation and temperature
    elif df_evapot_cond == 'None':
        #--------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        #Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            arr_p = df_precip_sup.T.loc[df_precip_sup.T.index == i].to_numpy()
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_p))  +'\n')  

        #Temperatura
        for j in tempGet:
            arr_t = df_tempSup.T.loc[df_tempSup.T.index == j].to_numpy()
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')  

    #Todos
    else:
        #--------------------
        Tetis_file.write("G               "+str(len(df_precip_sup))+"         1440\n")
        #Tetis_file.write("*         dd-mm-aaaa  hh:mm\n")
        Tetis_file.write("F           01-01-2000      00:00\n")

        #---------------------COLOCAR LOS DATOS DE UBICACION DE LOS PUNTOS O ESTACIONES------------------------------------------------------
        #Precipitacion
        for i in precpGet:
            arr_p = df_precip_sup.T.loc[df_precip_sup.T.index == i].to_numpy()
            Tetis_file.write('P         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == i,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_p))  +'\n')  

        #Temperatura
        for j in tempGet:
            arr_t = df_tempSup.T.loc[df_tempSup.T.index == j].to_numpy()
            Tetis_file.write('T         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == j,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')  

        #Evapotranspiration
        for k in option5_evapot:
            arr_t = df_evapot.T.loc[df_evapot.T.index == k].to_numpy()
            Tetis_file.write('E         "'+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'CODIGO'].values[0])   +'" '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'latitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'longitud'].values[0])   +' '+str(df_ubi_info.loc[df_ubi_info['CODIGO'] == k,'altitud'].values[0])+' '+ (' '.join(' '.join('%0.2f' %x for x in y) for y in arr_t))  +'\n')


    Tetis_file.close()
    return Tetis_file




st.header('Bienvenido a ClimaData') 



(''' 
Gestión información climatológcia del Tolima 
''')

col1, col2 = st.columns(2)

with col1:
    st.header('Datos de Precipitación') 

    (''' 
    ### Estaciones en superficie 
    ''')

    df_precip_sup = pd.read_csv('https://raw.githubusercontent.com/IngButters/ClimaData/master/est_sup_precip_fase_2.csv')
    df_precip_sup.columns = df_precip_sup.columns.astype(str)
    df_precip_sup = df_precip_sup.round(decimals=2)
    df_precip_sup

    option1_precip_sup = st.multiselect(
        'Seleccione la(s) estaciones a consultar',
        df_precip_sup.columns.tolist()[1:])


    st.write('Usted Seleccionó:', option1_precip_sup)

    #for j in option:
        #st.write(str(i))
    #    st.line_chart(data=df_precip_sup, x='fecha', y=str(j), width=0, height=0, use_container_width=True)


  #  ( Estaciones en satélite   )

#    df_precip_sat = pd.read_csv('https://raw.githubusercontent.com/IngButters/ClimaData/master/puntos_sat_precip_F2.csv')
#    df_precip_sat = df_precip_sat.round(decimals=2)
#    df_precip_sat

#    option2 = st.multiselect(
#        'Seleccione la(s) estaciones a consultar',
#        ['Ninguno'] + df_precip_sat.columns.tolist()[1:])

#    if 'Ninguno' not in option2:
#        st.write('Usted Seleccionó:', option2)

    #for j in option:
        #st.write(str(i))
    #    st.line_chart(data=df_precip_sup, x='fecha', y=str(j), width=0, height=0, use_container_width=True)






with col2:
    st.header('Datos de Temperatura') 

    (''' 
    ### Estaciones en superficie
    ''')

    df_temp_sup = pd.read_csv('https://raw.githubusercontent.com/IngButters/ClimaData/master/est_sup_temp_fase_2.csv')
    df_temp_sup = df_temp_sup.round(decimals=2)
    df_temp_sup.columns = df_temp_sup.columns.astype(str)
    df_temp_sup

    option3_temp_sup = st.multiselect(
        'Seleccione la(s) estaciones a consultar',
        df_temp_sup.columns.tolist()[1:])


    st.write('Usted Seleccionó:', option3_temp_sup)

    #for i in option:
        #st.write(str(i))
     #   st.line_chart(data=df_temp_sup, x='fecha', y=str(i), width=0, height=0, use_container_width=True)


    #(   ### Estaciones en satélite)

#    df_temp_sat = pd.read_csv('https://raw.githubusercontent.com/IngButters/ClimaData/master/puntos_temp_F2.csv')
#    df_temp_sat = df_temp_sat.round(decimals=2)
#    df_temp_sat

#    option4 = st.multiselect(
#        'Seleccione la(s) estaciones a consultar',
#        ['Ninguno'] + df_temp_sat.columns.tolist()[1:])
    
#    if 'Ninguno' not in option4:
#        st.write('Usted Seleccionó:', option4)

    #for i in option:
        #st.write(str(i))
     #   st.line_chart(data=df_temp_sup, x='fecha', y=str(i), width=0, height=0, use_container_width=True)


st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

#st.markdown(":heavy_minus_sign:" * 50)

(''' 
--- 
''')

st.header('Datos de Evapotranspiración') 

(''' 
### Estaciones en superficie
''')

df_evapot_sup = pd.read_csv('https://raw.githubusercontent.com/IngButters/ClimaData/master/estaciones_sup_evapot.csv')#, usecols=cols_evapot[0:1])
df_evapot_sup = df_evapot_sup.round(decimals=2)
#df_evapot_sup.columns = df_temp_sup.columns.astype(str)

option5_evapot = st.multiselect(
    'Seleccione la(s) estaciones a consultar',
     df_evapot_sup)

#if 'Ninguno' not in option5_evapot:
option5_evapot = [str(item) for item in option5_evapot]

st.write('Usted Seleccionó:', option5_evapot)




if len(option5_evapot) > 0:
    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

    #df_datos_evapot.columns = df_datos_evapot.columns.astype(str)
    df_ub2 = df_ub.set_index('CODIGO')

    df_datos_evapot = calcEvapotranspiracion(df_datos_evapot, df_ub2, df_radiacion, option5_evapot)
    df_evapot_sup = df_datos_evapot.round(decimals=2)





st.markdown("""<hr style="height:2px;border:none;color:#333;background-color:#333;" /> """, unsafe_allow_html=True)

#st.markdown(":heavy_minus_sign:" * 50)

(''' 
--- 
''')

st.header('Generar escenarios de Cambio Climático') 
(''' 
En este apartado se generan los archivos columna y CEDEX
''')


col3, col4 = st.columns(2)


with col3:
    option6_CC = st.selectbox(
        'Generar escenarios de Cambio Climático',
        ('No', 'Si'))
    st.write('Usted Seleccionó:', option6_CC)






#----------------------------------------------------------Si Cambio Climático--------------------------------

with col4:
   if 'Si' in option6_CC: # If user selects Si  do 👇
        option7_anu_tri = st.selectbox(
        'Seleccione la proyección temporal',
        ('Anual', 'Trimestral'))
        

if 'Si' in option6_CC: # If user selects Si  do 👇
    option8_RCP = st.selectbox(
    'Seleccione el RCP',
    ('2.6', '4.5', '6.0', '8.5', 'Ensamble'))

option9_cedex_col = st.selectbox(
'Seleccione el formato de las series',
('Columna', 'Cedex'))




# Create a button to download the file
if st.button('Generar Archivo'):

    #----------------------------------------------------------No Cambio Climático--------------------------------
    if 'No' in option6_CC: # If user selects Si  do 👇
        st.write('### 👇 Al aparecer el botón puede descargar sus archivos 👇')
        
        #option3_temp_sup
       

        #Seleccion = Ninguna en precipitacion y evapotranspiracion
        if not option1_precip_sup  and  not option5_evapot:
            
            #--------------------------Lectura datos de temperatura---------------------------------------
            df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
            df_tempSup = df_tempSup.fillna(-99)


            option1_precip_sup = 'None'
            option5_evapot = 'None'
            df_precipSup = option1_precip_sup

            df_evapot = option5_evapot

            #--------------------------------Generar archivo Tetis-----------------------------------------------
            if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇
                arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'soloTempColumna')
                with open('soloTempColumna.txt', 'r') as f:
                    arch_columna2 = f.read()
                #st.write(arch_columna2)
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='soloTempColumna.txt',mime="text/plain")

            if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇
                arch_columna = archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'soloTempCEDEX')
                with open('soloTempCEDEX.txt', 'r') as f:
                    arch_columna2 = f.read()
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='soloTempCEDEX.txt')


        #Seleccion = Ninguna en temperatura y evapotranspiracion
        elif not option3_temp_sup and  not option5_evapot:
            #--------------------------Lectura datos de precipitación-------------------------------------
            df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)
            df_precipSup = df_precipSup.fillna(-1)

            option3_temp_sup = 'None'
            df_tempSup = option3_temp_sup

            option5_evapot = 'None'
            df_evapot = option5_evapot

            #--------------------------------Generar archivo Tetis-----------------------------------------------
            if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇
                arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'soloPrecipColumna')
                with open('soloPrecipColumna.txt', 'r') as f:
                    arch_columna2 = f.read()
                #st.write(arch_columna2)
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='soloPrecipColumna.txt',mime="text/plain")

            if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇
                arch_columna = archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'soloPrecipCEDEX')
                with open('soloPrecipCEDEX.txt', 'r') as f:
                    arch_columna2 = f.read()
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='soloPrecipCEDEX.txt')

        #Seleccion = Ninguna en evapotranspiracion
        elif not option5_evapot:
            #--------------------------Lectura datos de precipitación-------------------------------------
            df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)
            df_precipSup = df_precipSup.fillna(-1)

            #--------------------------Lectura datos de temperatura---------------------------------------
            df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
            df_tempSup = df_tempSup.fillna(-99)

            option5_evapot = 'None'
            df_evapot = option5_evapot

            #--------------------------------Generar archivo Tetis-----------------------------------------------
            if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇
                arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'precipYtempColumna')
                with open('precipYtempColumna.txt', 'r') as f:
                    arch_columna2 = f.read()
                #st.write(arch_columna2)
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='precipYtempColumna.txt',mime="text/plain")

            if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇
                arch_columna = archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'precipYtempCEDEX')
                with open('precipYtempCEDEX.txt', 'r') as f:
                    arch_columna2 = f.read()
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='precipYtempCEDEX.txt')

        # Ninguna en precipitacion y temperatura
        elif not option3_temp_sup and not option1_precip_sup:
            #----------------Evapotranspiracion--------------------
            df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
            df_ub2 = df_ub.set_index('CODIGO')
            df_evapot = calcEvapotranspiracion(df_datos_evapot, df_ub2, df_radiacion, option5_evapot)

            option3_temp_sup = 'None'
            df_tempSup = option3_temp_sup

            option1_precip_sup = 'None'
            df_precipSup = option1_precip_sup

            
            #--------------------------------Generar archivo Tetis-----------------------------------------------
            if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇
                arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'soloEvapotColumna')
                with open('soloEvapotColumna.txt', 'r') as f:
                    arch_columna2 = f.read()
                #st.write(arch_columna2)
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='soloEvapotColumna.txt',mime="text/plain")

            if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇
                arch_columna = archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'soloEvapotCEDEX')
                with open('soloEvapotCEDEX.txt', 'r') as f:
                    arch_columna2 = f.read()
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='soloEvapotCEDEX.txt')

        #Ninguna en precipitacion
        elif not option1_precip_sup:
            #--------------------------Lectura datos de temperatura---------------------------------------
            df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
            df_tempSup = df_tempSup.fillna(-99)

            #----------------Evapotranspiracion--------------------
            df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
            df_ub2 = df_ub.set_index('CODIGO')
            df_evapot = calcEvapotranspiracion(df_datos_evapot, df_ub2, df_radiacion, option5_evapot)

            option1_precip_sup = 'None'
            df_precipSup = option1_precip_sup

            #--------------------------------Generar archivo Tetis-----------------------------------------------
            if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇
                arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'TempeEvapotColumna')
                with open('TempeEvapotColumna.txt', 'r') as f:
                    arch_columna2 = f.read()
                #st.write(arch_columna2)
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='TempeEvapotColumna.txt',mime="text/plain")

            if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇
                arch_columna = archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'TempeEvapotCEDEX')
                with open('TempeEvapotCEDEX.txt', 'r') as f:
                    arch_columna2 = f.read()
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='TempeEvapotCEDEX.txt')


        #Seleccion = Ninguna en temperatura
        elif not option3_temp_sup:

            #----------------Evapotranspiracion--------------------
            df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
            df_ub2 = df_ub.set_index('CODIGO')
            df_evapot = calcEvapotranspiracion(df_datos_evapot, df_ub2, df_radiacion, option5_evapot)  

             #--------------------------Lectura datos de precipitación-------------------------------------
            df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)
            df_precipSup = df_precipSup.fillna(-1)    

            option3_temp_sup = 'None'
            df_tempSup = option3_temp_sup   


            #--------------------------------Generar archivo Tetis-----------------------------------------------
            if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇
                arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'PrecipEvapotColumna')
                with open('PrecipEvapotColumna.txt', 'r') as f:
                    arch_columna2 = f.read()
                #st.write(arch_columna2)
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='PrecipEvapotColumna.txt',mime="text/plain")

            if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇
                arch_columna = archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'PrecipEvapotCEDEX')
                with open('PrecipEvapotCEDEX.txt', 'r') as f:
                    arch_columna2 = f.read()
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='PrecipEvapotCEDEX.txt')   

        else:
            #----------------Evapotranspiracion--------------------
            df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
            df_ub2 = df_ub.set_index('CODIGO')
            df_evapot = calcEvapotranspiracion(df_datos_evapot, df_ub2, df_radiacion, option5_evapot)  

             #--------------------------Lectura datos de precipitación-------------------------------------
            df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)
            df_precipSup = df_precipSup.fillna(-1)  

            #--------------------------Lectura datos de temperatura---------------------------------------
            df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
            df_tempSup = df_tempSup.fillna(-99)

            #--------------------------------Generar archivo Tetis-----------------------------------------------
            if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇
                arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'PrecipTempEvapotColumna')
                with open('PrecipTempEvapotColumna.txt', 'r') as f:
                    arch_columna2 = f.read()
                #st.write(arch_columna2)
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='PrecipTempEvapotColumna.txt',mime="text/plain")

            if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇
                arch_columna = archivoCEDEX(df_precipSup, df_tempSup, df_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'PrecipTempEvapotCEDEX')
                with open('PrecipTempEvapotCEDEX.txt', 'r') as f:
                    arch_columna2 = f.read()
                st.download_button(label='Descargar Archivo',data=arch_columna2, file_name='PrecipTempEvapotCEDEX.txt')  


    #----------------------------------------------------------Si Cambio Climático--------------------------------
    if 'Si' in option6_CC: # If user selects Si  do 👇
        st.write('### 👇 Al aparecer el botón puede descargar sus archivos 👇')
        
        #option3_temp_sup
       

        #Anual
        if option7_anu_tri == 'Anual':
            if option8_RCP == '2.6':
                #Ninguna precipitacion
                if not option1_precip_sup and option3_temp_sup and option5_evapot:
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)


                    df_tempSup_2011_2040 = df_tempSup + 0.89

                    df_tempSup_2041_2070 = df_tempSup + 1.26

                    df_tempSup_2071_2100 = df_tempSup + 1.22

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 0.89
                    df_evapo_2041_2070 = df_datos_evapot + 1.26
                    df_evapo_2071_2100 = df_datos_evapot + 1.22


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  


                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_tempEvapot_2011_2040Columna')
                        with open('anual_2_6_tempEvapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_tempEvapot_2041_2070Columna')
                        with open('anual_2_6_tempEvapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_tempEvapot_2071_2100Columna')
                        with open('anual_2_6_tempEvapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_tempEvapot_2011_2040Columna.txt', 'anual_2_6_tempEvapot_2041_2070Columna.txt', 'anual_2_6_tempEvapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_tempEvapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_tempEvapot_2011_2040cedex')
                        with open('anual_2_6_tempEvapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_tempEvapot_2041_2070cedex')
                        with open('anual_2_6_tempEvapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_tempEvapot_2071_2100cedex')
                        with open('anual_2_6_tempEvapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_tempEvapot_2011_2040cedex.txt', 'anual_2_6_tempEvapot_2041_2070cedex.txt', 'anual_2_6_tempEvapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_tempEvapotcedex.zip", mime="application/zip")

                #Ninguna temperatura
                elif option1_precip_sup and not option3_temp_sup and option5_evapot:    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.0936
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1320
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.0855
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 0.89
                    df_evapo_2041_2070 = df_datos_evapot + 1.26
                    df_evapo_2071_2100 = df_datos_evapot + 1.22


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipEvapott_2011_2040Columna')
                        with open('anual_2_6_precipEvapott_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipEvapott_2041_2070Columna')
                        with open('anual_2_6_precipEvapott_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipEvapott_2071_2100Columna')
                        with open('anual_2_6_precipEvapott_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_precipEvapott_2011_2040Columna.txt', 'anual_2_6_precipEvapott_2041_2070Columna.txt', 'anual_2_6_precipEvapott_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_precipEvapottColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipEvapott_2011_2040cedex')
                        with open('anual_2_6_precipEvapott_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipEvapott_2041_2070cedex')
                        with open('anual_2_6_precipEvapott_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipEvapott_2071_2100cedex')
                        with open('anual_2_6_precipEvapott_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_precipEvapott_2011_2040cedex.txt', 'anual_2_6_precipEvapott_2041_2070cedex.txt', 'anual_2_6_precipEvapott_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_precipEvapottcedex.zip", mime="application/zip")

                #Ninguna evapotranspiracion
                elif option1_precip_sup and option3_temp_sup and not option5_evapot:
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    df_precipSup_2011_2040 = df_precipSup * 1.0936
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1320
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.0855
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)


                    df_tempSup_2011_2040 = df_tempSup + 0.89

                    df_tempSup_2041_2070 = df_tempSup + 1.26

                    df_tempSup_2071_2100 = df_tempSup + 1.22

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipTemp_2011_2040Columna')
                        with open('anual_2_6_precipTemp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipTemp_2041_2070Columna')
                        with open('anual_2_6_precipTemp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipTemp_2071_2100Columna')
                        with open('anual_2_6_precipTemp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_precipTemp_2011_2040Columna.txt', 'anual_2_6_precipTemp_2041_2070Columna.txt', 'anual_2_6_precipTemp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_precipTempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipTemp_2011_2040cedex')
                        with open('anual_2_6_precipTemp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipTemp_2041_2070cedex')
                        with open('anual_2_6_precipTemp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precipTemp_2071_2100cedex')
                        with open('anual_2_6_precipTemp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_precipTemp_2011_2040cedex.txt', 'anual_2_6_precipTemp_2041_2070cedex.txt', 'anual_2_6_precipTemp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_precipTempcedex.zip", mime="application/zip")


                #Solo temperatura
                elif not option1_precip_sup and option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)


                    df_tempSup_2011_2040 = df_tempSup + 0.89

                    df_tempSup_2041_2070 = df_tempSup + 1.26

                    df_tempSup_2071_2100 = df_tempSup + 1.22

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_temp_2011_2040Columna')
                        with open('anual_2_6_temp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_temp_2041_2070Columna')
                        with open('anual_2_6_temp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_temp_2071_2100Columna')
                        with open('anual_2_6_temp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_temp_2011_2040Columna.txt', 'anual_2_6_temp_2041_2070Columna.txt', 'anual_2_6_temp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_tempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_temp_2011_2040cedex')
                        with open('anual_2_6_temp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_temp_2041_2070cedex')
                        with open('anual_2_6_temp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_temp_2071_2100cedex')
                        with open('anual_2_6_temp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_temp_2011_2040cedex.txt', 'anual_2_6_temp_2041_2070cedex.txt', 'anual_2_6_temp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_tempcedex.zip", mime="application/zip")

                #Solo precipitación
                elif option1_precip_sup and not option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.0936
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1320
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.0855
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99) 

                    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precip_2011_2040Columna')
                        with open('anual_2_6_precip_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precip_2041_2070Columna')
                        with open('anual_2_6_precip_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precip_2071_2100Columna')
                        with open('anual_2_6_precip_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_precip_2011_2040Columna.txt', 'anual_2_6_precip_2041_2070Columna.txt', 'anual_2_6_precip_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_precipColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precip_2011_2040cedex')
                        with open('anual_2_6_precip_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precip_2041_2070cedex')
                        with open('anual_2_6_precip_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_precip_2071_2100cedex')
                        with open('anual_2_6_precip_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_precip_2011_2040cedex.txt', 'anual_2_6_precip_2041_2070cedex.txt', 'anual_2_6_precip_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_precipcedex.zip", mime="application/zip")

                #Solo evapotranspiracion
                if not option1_precip_sup and not option3_temp_sup and  option5_evapot:

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup
                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 0.89
                    df_evapo_2041_2070 = df_datos_evapot + 1.26
                    df_evapo_2071_2100 = df_datos_evapot + 1.22


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_evapot_2011_2040Columna')
                        with open('anual_2_6_evapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_evapot_2041_2070Columna')
                        with open('anual_2_6_evapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_evapot_2071_2100Columna')
                        with open('anual_2_6_evapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_evapot_2011_2040Columna.txt', 'anual_2_6_evapot_2041_2070Columna.txt', 'anual_2_6_evapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_evapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_evapot_2011_2040cedex')
                        with open('anual_2_6_evapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_evapot_2041_2070cedex')
                        with open('anual_2_6_evapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_evapot_2071_2100cedex')
                        with open('anual_2_6_evapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_evapot_2011_2040cedex.txt', 'anual_2_6_evapot_2041_2070cedex.txt', 'anual_2_6_evapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_evapotcedex.zip", mime="application/zip")


                # todos los options
                elif  option1_precip_sup and  option3_temp_sup and  option5_evapot:    
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 0.89
                    df_evapo_2041_2070 = df_datos_evapot + 1.26
                    df_evapo_2071_2100 = df_datos_evapot + 1.22


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)



                    df_precipSup_2011_2040 = df_precipSup * 1.0936
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1320
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.0855
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)                                                       

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
             

                    df_tempSup_2011_2040 = df_tempSup + 0.89

                    df_tempSup_2041_2070 = df_tempSup + 1.26

                    df_tempSup_2071_2100 = df_tempSup + 1.22

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_todos_2011_2040Columna')
                        with open('anual_2_6_todos_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_todos_2041_2070Columna')
                        with open('anual_2_6_todos_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_todos_2071_2100Columna')
                        with open('anual_2_6_todos_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_todos_2011_2040Columna.txt', 'anual_2_6_todos_2041_2070Columna.txt', 'anual_2_6_todos_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_todosColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_todos_2011_2040cedex')
                        with open('anual_2_6_todos_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_todos_2041_2070cedex')
                        with open('anual_2_6_todos_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_2_6_todos_2071_2100cedex')
                        with open('anual_2_6_todos_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_2_6_todos_2011_2040cedex.txt', 'anual_2_6_todos_2041_2070cedex.txt', 'anual_2_6_todos_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_2_6_todoscedex.zip", mime="application/zip")

            elif option8_RCP == '4.5':
                #Ninguna precipitacion
                if not option1_precip_sup and option3_temp_sup and option5_evapot:
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)



                    df_tempSup_2011_2040 = df_tempSup + 1.01

                    df_tempSup_2041_2070 = df_tempSup + 1.79

                    df_tempSup_2071_2100 = df_tempSup + 2.01

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.01
                    df_evapo_2041_2070 = df_datos_evapot + 1.79
                    df_evapo_2071_2100 = df_datos_evapot + 2.01


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  


                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_tempEvapot_2011_2040Columna')
                        with open('anual_4_5_tempEvapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_tempEvapot_2041_2070Columna')
                        with open('anual_4_5_tempEvapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_tempEvapot_2071_2100Columna')
                        with open('anual_4_5_tempEvapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_tempEvapot_2011_2040Columna.txt', 'anual_4_5_tempEvapot_2041_2070Columna.txt', 'anual_4_5_tempEvapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_tempEvapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_tempEvapot_2011_2040cedex')
                        with open('anual_4_5_tempEvapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_tempEvapot_2041_2070cedex')
                        with open('anual_4_5_tempEvapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_tempEvapot_2071_2100cedex')
                        with open('anual_4_5_tempEvapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_tempEvapot_2011_2040cedex.txt', 'anual_4_5_tempEvapot_2041_2070cedex.txt', 'anual_4_5_tempEvapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_tempEvapotcedex.zip", mime="application/zip")

                #Ninguna temperatura
                elif option1_precip_sup and not option3_temp_sup and option5_evapot:    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1089
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1221
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1425
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.01
                    df_evapo_2041_2070 = df_datos_evapot + 1.79
                    df_evapo_2071_2100 = df_datos_evapot + 2.01


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipEvapott_2011_2040Columna')
                        with open('anual_4_5_precipEvapott_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipEvapott_2041_2070Columna')
                        with open('anual_4_5_precipEvapott_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipEvapott_2071_2100Columna')
                        with open('anual_4_5_precipEvapott_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_precipEvapott_2011_2040Columna.txt', 'anual_4_5_precipEvapott_2041_2070Columna.txt', 'anual_4_5_precipEvapott_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_precipEvapottColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipEvapott_2011_2040cedex')
                        with open('anual_4_5_precipEvapott_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipEvapott_2041_2070cedex')
                        with open('anual_4_5_precipEvapott_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipEvapott_2071_2100cedex')
                        with open('anual_4_5_precipEvapott_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_precipEvapott_2011_2040cedex.txt', 'anual_4_5_precipEvapott_2041_2070cedex.txt', 'anual_4_5_precipEvapott_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_precipEvapottcedex.zip", mime="application/zip")

                #Ninguna evapotranspiracion
                elif option1_precip_sup and option3_temp_sup and not option5_evapot:
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    df_precipSup_2011_2040 = df_precipSup * 1.1089
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1221
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1425
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1) 

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)


                    df_tempSup_2011_2040 = df_tempSup + 1.01
                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup + 1.79
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup + 2.01
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipTemp_2011_2040Columna')
                        with open('anual_4_5_precipTemp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipTemp_2041_2070Columna')
                        with open('anual_4_5_precipTemp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipTemp_2071_2100Columna')
                        with open('anual_4_5_precipTemp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_precipTemp_2011_2040Columna.txt', 'anual_4_5_precipTemp_2041_2070Columna.txt', 'anual_4_5_precipTemp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_precipTempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipTemp_2011_2040cedex')
                        with open('anual_4_5_precipTemp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipTemp_2041_2070cedex')
                        with open('anual_4_5_precipTemp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precipTemp_2071_2100cedex')
                        with open('anual_4_5_precipTemp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_precipTemp_2011_2040cedex.txt', 'anual_4_5_precipTemp_2041_2070cedex.txt', 'anual_4_5_precipTemp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_precipTempcedex.zip", mime="application/zip")


                #Solo temperatura
                elif not option1_precip_sup and option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    

                    df_tempSup_2011_2040 = df_tempSup + 1.01
                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup + 1.79
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup + 2.01
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_temp_2011_2040Columna')
                        with open('anual_4_5_temp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_temp_2041_2070Columna')
                        with open('anual_4_5_temp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_temp_2071_2100Columna')
                        with open('anual_4_5_temp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_temp_2011_2040Columna.txt', 'anual_4_5_temp_2041_2070Columna.txt', 'anual_4_5_temp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_tempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_temp_2011_2040cedex')
                        with open('anual_4_5_temp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_temp_2041_2070cedex')
                        with open('anual_4_5_temp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_temp_2071_2100cedex')
                        with open('anual_4_5_temp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_temp_2011_2040cedex.txt', 'anual_4_5_temp_2041_2070cedex.txt', 'anual_4_5_temp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_tempcedex.zip", mime="application/zip")

                #Solo precipitación
                elif option1_precip_sup and not option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1089
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1221
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1425
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   
                    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precip_2011_2040Columna')
                        with open('anual_4_5_precip_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precip_2041_2070Columna')
                        with open('anual_4_5_precip_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precip_2071_2100Columna')
                        with open('anual_4_5_precip_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_precip_2011_2040Columna.txt', 'anual_4_5_precip_2041_2070Columna.txt', 'anual_4_5_precip_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_precipColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precip_2011_2040cedex')
                        with open('anual_4_5_precip_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precip_2041_2070cedex')
                        with open('anual_4_5_precip_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_precip_2071_2100cedex')
                        with open('anual_4_5_precip_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_precip_2011_2040cedex.txt', 'anual_4_5_precip_2041_2070cedex.txt', 'anual_4_5_precip_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_precipcedex.zip", mime="application/zip")

                #Solo evapotranspiracion
                if not option1_precip_sup and not option3_temp_sup and  option5_evapot:

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup
                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.01
                    df_evapo_2041_2070 = df_datos_evapot + 1.79
                    df_evapo_2071_2100 = df_datos_evapot + 2.01


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_evapot_2011_2040Columna')
                        with open('anual_4_5_evapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_evapot_2041_2070Columna')
                        with open('anual_4_5_evapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_evapot_2071_2100Columna')
                        with open('anual_4_5_evapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_evapot_2011_2040Columna.txt', 'anual_4_5_evapot_2041_2070Columna.txt', 'anual_4_5_evapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_evapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_evapot_2011_2040cedex')
                        with open('anual_4_5_evapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_evapot_2041_2070cedex')
                        with open('anual_4_5_evapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_evapot_2071_2100cedex')
                        with open('anual_4_5_evapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_evapot_2011_2040cedex.txt', 'anual_4_5_evapot_2041_2070cedex.txt', 'anual_4_5_evapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_evapotcedex.zip", mime="application/zip")


                # todos los options
                elif  option1_precip_sup and  option3_temp_sup and  option5_evapot:    
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.01
                    df_evapo_2041_2070 = df_datos_evapot + 1.79
                    df_evapo_2071_2100 = df_datos_evapot + 2.01


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)


                    df_precipSup_2011_2040 = df_precipSup * 1.1089
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1221
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1425
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)                            

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)


                    df_tempSup_2011_2040 = df_tempSup + 1.01
                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup + 1.79
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup + 2.01
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_todos_2011_2040Columna')
                        with open('anual_4_5_todos_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_todos_2041_2070Columna')
                        with open('anual_4_5_todos_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_todos_2071_2100Columna')
                        with open('anual_4_5_todos_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_todos_2011_2040Columna.txt', 'anual_4_5_todos_2041_2070Columna.txt', 'anual_4_5_todos_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_todosColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_todos_2011_2040cedex')
                        with open('anual_4_5_todos_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_todos_2041_2070cedex')
                        with open('anual_4_5_todos_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_4_5_todos_2071_2100cedex')
                        with open('anual_4_5_todos_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_4_5_todos_2011_2040cedex.txt', 'anual_4_5_todos_2041_2070cedex.txt', 'anual_4_5_todos_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_4_5_todoscedex.zip", mime="application/zip")

            elif option8_RCP == '6.0':
                #Ninguna precipitacion
                if not option1_precip_sup and option3_temp_sup and option5_evapot:
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)


                    df_tempSup_2011_2040 = df_tempSup + 0.88

                    df_tempSup_2041_2070 = df_tempSup + 1.58

                    df_tempSup_2071_2100 = df_tempSup + 2.32

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 0.88
                    df_evapo_2041_2070 = df_datos_evapot + 1.58
                    df_evapo_2071_2100 = df_datos_evapot + 2.32


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  


                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_tempEvapot_2011_2040Columna')
                        with open('anual_6_0_tempEvapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_tempEvapot_2041_2070Columna')
                        with open('anual_6_0_tempEvapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_tempEvapot_2071_2100Columna')
                        with open('anual_6_0_tempEvapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_tempEvapot_2011_2040Columna.txt', 'anual_6_0_tempEvapot_2041_2070Columna.txt', 'anual_6_0_tempEvapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_tempEvapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_tempEvapot_2011_2040cedex')
                        with open('anual_6_0_tempEvapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_tempEvapot_2041_2070cedex')
                        with open('anual_6_0_tempEvapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_tempEvapot_2071_2100cedex')
                        with open('anual_6_0_tempEvapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_tempEvapot_2011_2040cedex.txt', 'anual_6_0_tempEvapot_2041_2070cedex.txt', 'anual_6_0_tempEvapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_tempEvapotcedex.zip", mime="application/zip")

                #Ninguna temperatura
                elif option1_precip_sup and not option3_temp_sup and option5_evapot:    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1054
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1311
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1724
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)  

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 0.88
                    df_evapo_2041_2070 = df_datos_evapot + 1.58
                    df_evapo_2071_2100 = df_datos_evapot + 2.32

                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipEvapott_2011_2040Columna')
                        with open('anual_6_0_precipEvapott_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipEvapott_2041_2070Columna')
                        with open('anual_6_0_precipEvapott_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipEvapott_2071_2100Columna')
                        with open('anual_6_0_precipEvapott_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_precipEvapott_2011_2040Columna.txt', 'anual_6_0_precipEvapott_2041_2070Columna.txt', 'anual_6_0_precipEvapott_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_precipEvapottColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipEvapott_2011_2040cedex')
                        with open('anual_6_0_precipEvapott_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipEvapott_2041_2070cedex')
                        with open('anual_6_0_precipEvapott_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipEvapott_2071_2100cedex')
                        with open('anual_6_0_precipEvapott_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_precipEvapott_2011_2040cedex.txt', 'anual_6_0_precipEvapott_2041_2070cedex.txt', 'anual_6_0_precipEvapott_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_precipEvapottcedex.zip", mime="application/zip")

                #Ninguna evapotranspiracion
                elif option1_precip_sup and option3_temp_sup and not option5_evapot:
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    df_precipSup_2011_2040 = df_precipSup * 1.1054
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1311
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1724
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 0.88

                    df_tempSup_2041_2070 = df_tempSup + 1.58

                    df_tempSup_2071_2100 = df_tempSup + 2.32

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipTemp_2011_2040Columna')
                        with open('anual_6_0_precipTemp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipTemp_2041_2070Columna')
                        with open('anual_6_0_precipTemp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipTemp_2071_2100Columna')
                        with open('anual_6_0_precipTemp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_precipTemp_2011_2040Columna.txt', 'anual_6_0_precipTemp_2041_2070Columna.txt', 'anual_6_0_precipTemp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_precipTempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipTemp_2011_2040cedex')
                        with open('anual_6_0_precipTemp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipTemp_2041_2070cedex')
                        with open('anual_6_0_precipTemp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precipTemp_2071_2100cedex')
                        with open('anual_6_0_precipTemp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_precipTemp_2011_2040cedex.txt', 'anual_6_0_precipTemp_2041_2070cedex.txt', 'anual_6_0_precipTemp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_precipTempcedex.zip", mime="application/zip")


                #Solo temperatura
                elif not option1_precip_sup and option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 0.88

                    df_tempSup_2041_2070 = df_tempSup + 1.58

                    df_tempSup_2071_2100 = df_tempSup + 2.32

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_temp_2011_2040Columna')
                        with open('anual_6_0_temp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_temp_2041_2070Columna')
                        with open('anual_6_0_temp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_temp_2071_2100Columna')
                        with open('anual_6_0_temp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_temp_2011_2040Columna.txt', 'anual_6_0_temp_2041_2070Columna.txt', 'anual_6_0_temp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_tempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_temp_2011_2040cedex')
                        with open('anual_6_0_temp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_temp_2041_2070cedex')
                        with open('anual_6_0_temp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_temp_2071_2100cedex')
                        with open('anual_6_0_temp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_temp_2011_2040cedex.txt', 'anual_6_0_temp_2041_2070cedex.txt', 'anual_6_0_temp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_tempcedex.zip", mime="application/zip")

                #Solo precipitación
                elif option1_precip_sup and not option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1054
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1311
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1724
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)  

                    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precip_2011_2040Columna')
                        with open('anual_6_0_precip_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precip_2041_2070Columna')
                        with open('anual_6_0_precip_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precip_2071_2100Columna')
                        with open('anual_6_0_precip_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_precip_2011_2040Columna.txt', 'anual_6_0_precip_2041_2070Columna.txt', 'anual_6_0_precip_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_precipColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precip_2011_2040cedex')
                        with open('anual_6_0_precip_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precip_2041_2070cedex')
                        with open('anual_6_0_precip_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_precip_2071_2100cedex')
                        with open('anual_6_0_precip_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_precip_2011_2040cedex.txt', 'anual_6_0_precip_2041_2070cedex.txt', 'anual_6_0_precip_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_precipcedex.zip", mime="application/zip")

                #Solo evapotranspiracion
                if not option1_precip_sup and not option3_temp_sup and  option5_evapot:

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup
                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 0.88
                    df_evapo_2041_2070 = df_datos_evapot + 1.58
                    df_evapo_2071_2100 = df_datos_evapot + 2.32


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_evapot_2011_2040Columna')
                        with open('anual_6_0_evapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_evapot_2041_2070Columna')
                        with open('anual_6_0_evapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_evapot_2071_2100Columna')
                        with open('anual_6_0_evapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_evapot_2011_2040Columna.txt', 'anual_6_0_evapot_2041_2070Columna.txt', 'anual_6_0_evapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_evapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_evapot_2011_2040cedex')
                        with open('anual_6_0_evapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_evapot_2041_2070cedex')
                        with open('anual_6_0_evapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_evapot_2071_2100cedex')
                        with open('anual_6_0_evapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_evapot_2011_2040cedex.txt', 'anual_6_0_evapot_2041_2070cedex.txt', 'anual_6_0_evapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_evapotcedex.zip", mime="application/zip")


                # todos los options
                elif  option1_precip_sup and  option3_temp_sup and  option5_evapot:    
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 0.88
                    df_evapo_2041_2070 = df_datos_evapot + 1.58
                    df_evapo_2071_2100 = df_datos_evapot + 2.32


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)



                    df_precipSup_2011_2040 = df_precipSup * 1.1054
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1311
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1724
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)                          

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 0.88

                    df_tempSup_2041_2070 = df_tempSup + 1.58

                    df_tempSup_2071_2100 = df_tempSup + 2.32

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_todos_2011_2040Columna')
                        with open('anual_6_0_todos_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_todos_2041_2070Columna')
                        with open('anual_6_0_todos_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_todos_2071_2100Columna')
                        with open('anual_6_0_todos_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_todos_2011_2040Columna.txt', 'anual_6_0_todos_2041_2070Columna.txt', 'anual_6_0_todos_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_todosColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_todos_2011_2040cedex')
                        with open('anual_6_0_todos_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_todos_2041_2070cedex')
                        with open('anual_6_0_todos_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_6_0_todos_2071_2100cedex')
                        with open('anual_6_0_todos_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_6_0_todos_2011_2040cedex.txt', 'anual_6_0_todos_2041_2070cedex.txt', 'anual_6_0_todos_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_6_0_todoscedex.zip", mime="application/zip")


            elif option8_RCP == '8.5':
                #Ninguna precipitacion
                if not option1_precip_sup and option3_temp_sup and option5_evapot:
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 1.06

                    df_tempSup_2041_2070 = df_tempSup + 2.23

                    df_tempSup_2071_2100 = df_tempSup + 3.68

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.06
                    df_evapo_2041_2070 = df_datos_evapot + 2.23
                    df_evapo_2071_2100 = df_datos_evapot + 3.68

                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  


                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_tempEvapot_2011_2040Columna')
                        with open('anual_8_5_tempEvapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_tempEvapot_2041_2070Columna')
                        with open('anual_8_5_tempEvapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_tempEvapot_2071_2100Columna')
                        with open('anual_8_5_tempEvapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_tempEvapot_2011_2040Columna.txt', 'anual_8_5_tempEvapot_2041_2070Columna.txt', 'anual_8_5_tempEvapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_tempEvapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_tempEvapot_2011_2040cedex')
                        with open('anual_8_5_tempEvapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_tempEvapot_2041_2070cedex')
                        with open('anual_8_5_tempEvapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_tempEvapot_2071_2100cedex')
                        with open('anual_8_5_tempEvapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_tempEvapot_2011_2040cedex.txt', 'anual_8_5_tempEvapot_2041_2070cedex.txt', 'anual_8_5_tempEvapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_tempEvapotcedex.zip", mime="application/zip")

                #Ninguna temperatura
                elif option1_precip_sup and not option3_temp_sup and option5_evapot:    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1334
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1856
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1872
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)    

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.06
                    df_evapo_2041_2070 = df_datos_evapot + 2.23
                    df_evapo_2071_2100 = df_datos_evapot + 3.68


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipEvapott_2011_2040Columna')
                        with open('anual_8_5_precipEvapott_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipEvapott_2041_2070Columna')
                        with open('anual_8_5_precipEvapott_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipEvapott_2071_2100Columna')
                        with open('anual_8_5_precipEvapott_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_precipEvapott_2011_2040Columna.txt', 'anual_8_5_precipEvapott_2041_2070Columna.txt', 'anual_8_5_precipEvapott_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_precipEvapottColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipEvapott_2011_2040cedex')
                        with open('anual_8_5_precipEvapott_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipEvapott_2041_2070cedex')
                        with open('anual_8_5_precipEvapott_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipEvapott_2071_2100cedex')
                        with open('anual_8_5_precipEvapott_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_precipEvapott_2011_2040cedex.txt', 'anual_8_5_precipEvapott_2041_2070cedex.txt', 'anual_8_5_precipEvapott_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_precipEvapottcedex.zip", mime="application/zip")

                #Ninguna evapotranspiracion
                elif option1_precip_sup and option3_temp_sup and not option5_evapot:
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    df_precipSup_2011_2040 = df_precipSup * 1.1334
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1856
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1872
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)    

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 1.06

                    df_tempSup_2041_2070 = df_tempSup + 2.23

                    df_tempSup_2071_2100 = df_tempSup + 3.68

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipTemp_2011_2040Columna')
                        with open('anual_8_5_precipTemp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipTemp_2041_2070Columna')
                        with open('anual_8_5_precipTemp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipTemp_2071_2100Columna')
                        with open('anual_8_5_precipTemp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_precipTemp_2011_2040Columna.txt', 'anual_8_5_precipTemp_2041_2070Columna.txt', 'anual_8_5_precipTemp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_precipTempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipTemp_2011_2040cedex')
                        with open('anual_8_5_precipTemp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipTemp_2041_2070cedex')
                        with open('anual_8_5_precipTemp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precipTemp_2071_2100cedex')
                        with open('anual_8_5_precipTemp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_precipTemp_2011_2040cedex.txt', 'anual_8_5_precipTemp_2041_2070cedex.txt', 'anual_8_5_precipTemp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_precipTempcedex.zip", mime="application/zip")


                #Solo temperatura
                elif not option1_precip_sup and option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 1.06

                    df_tempSup_2041_2070 = df_tempSup + 2.23

                    df_tempSup_2071_2100 = df_tempSup + 3.68

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_temp_2011_2040Columna')
                        with open('anual_8_5_temp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_temp_2041_2070Columna')
                        with open('anual_8_5_temp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_temp_2071_2100Columna')
                        with open('anual_8_5_temp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_temp_2011_2040Columna.txt', 'anual_8_5_temp_2041_2070Columna.txt', 'anual_8_5_temp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_tempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_temp_2011_2040cedex')
                        with open('anual_8_5_temp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_temp_2041_2070cedex')
                        with open('anual_8_5_temp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_temp_2071_2100cedex')
                        with open('anual_8_5_temp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_temp_2011_2040cedex.txt', 'anual_8_5_temp_2041_2070cedex.txt', 'anual_8_5_temp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_tempcedex.zip", mime="application/zip")

                #Solo precipitación
                elif option1_precip_sup and not option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1334
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1856
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1872
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   

                    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precip_2011_2040Columna')
                        with open('anual_8_5_precip_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precip_2041_2070Columna')
                        with open('anual_8_5_precip_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precip_2071_2100Columna')
                        with open('anual_8_5_precip_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_precip_2011_2040Columna.txt', 'anual_8_5_precip_2041_2070Columna.txt', 'anual_8_5_precip_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_precipColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precip_2011_2040cedex')
                        with open('anual_8_5_precip_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precip_2041_2070cedex')
                        with open('anual_8_5_precip_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_precip_2071_2100cedex')
                        with open('anual_8_5_precip_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_precip_2011_2040cedex.txt', 'anual_8_5_precip_2041_2070cedex.txt', 'anual_8_5_precip_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_precipcedex.zip", mime="application/zip")

                #Solo evapotranspiracion
                elif not option1_precip_sup and not option3_temp_sup and  option5_evapot:

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup
                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.06
                    df_evapo_2041_2070 = df_datos_evapot + 2.23
                    df_evapo_2071_2100 = df_datos_evapot + 3.68


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_evapot_2011_2040Columna')
                        with open('anual_8_5_evapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_evapot_2041_2070Columna')
                        with open('anual_8_5_evapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_evapot_2071_2100Columna')
                        with open('anual_8_5_evapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_evapot_2011_2040Columna.txt', 'anual_8_5_evapot_2041_2070Columna.txt', 'anual_8_5_evapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_evapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_evapot_2011_2040cedex')
                        with open('anual_8_5_evapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_evapot_2041_2070cedex')
                        with open('anual_8_5_evapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_evapot_2071_2100cedex')
                        with open('anual_8_5_evapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_evapot_2011_2040cedex.txt', 'anual_8_5_evapot_2041_2070cedex.txt', 'anual_8_5_evapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_evapotcedex.zip", mime="application/zip")


                # todos los options
                elif  option1_precip_sup and  option3_temp_sup and  option5_evapot:    
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.06
                    df_evapo_2041_2070 = df_datos_evapot + 2.23
                    df_evapo_2071_2100 = df_datos_evapot + 3.68


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1334
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1856
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1872
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)                                      

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 1.06

                    df_tempSup_2041_2070 = df_tempSup + 2.23

                    df_tempSup_2071_2100 = df_tempSup + 3.68

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_todos_2011_2040Columna')
                        with open('anual_8_5_todos_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_todos_2041_2070Columna')
                        with open('anual_8_5_todos_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_todos_2071_2100Columna')
                        with open('anual_8_5_todos_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_todos_2011_2040Columna.txt', 'anual_8_5_todos_2041_2070Columna.txt', 'anual_8_5_todos_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_todosColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_todos_2011_2040cedex')
                        with open('anual_8_5_todos_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_todos_2041_2070cedex')
                        with open('anual_8_5_todos_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'anual_8_5_todos_2071_2100cedex')
                        with open('anual_8_5_todos_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['anual_8_5_todos_2011_2040cedex.txt', 'anual_8_5_todos_2041_2070cedex.txt', 'anual_8_5_todos_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="anual_8_5_todoscedex.zip", mime="application/zip")

            
            #trimestre
            elif option8_RCP == 'Ensamble':
                



                #Ninguna precipitacion
                if not option1_precip_sup and option3_temp_sup and option5_evapot:
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_ub2 = df_ub.set_index('CODIGO')

                    df_tempSup_2011_2040 = df_tempSup + 1.09

                    df_tempSup_2041_2070 = df_tempSup + 1.98

                    df_tempSup_2071_2100 = df_tempSup + 2.75

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.09
                    df_evapo_2041_2070 = df_datos_evapot + 1.98
                    df_evapo_2071_2100 = df_datos_evapot + 2.75
                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  


                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2011_2040Columna')
                        with open('Ensamble_tempEvapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2041_2070Columna')
                        with open('Ensamble_tempEvapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2071_2100Columna')
                        with open('Ensamble_tempEvapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_tempEvapot_2011_2040Columna.txt', 'Ensamble_tempEvapot_2041_2070Columna.txt', 'Ensamble_tempEvapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_tempEvapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2011_2040cedex')
                        with open('Ensamble_tempEvapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2041_2070cedex')
                        with open('Ensamble_tempEvapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2071_2100cedex')
                        with open('Ensamble_tempEvapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_tempEvapot_2011_2040cedex.txt', 'Ensamble_tempEvapot_2041_2070cedex.txt', 'Ensamble_tempEvapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_tempEvapotcedex.zip", mime="application/zip")

                #Ninguna temperatura
                elif option1_precip_sup and not option3_temp_sup and option5_evapot:    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1462
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1612
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1632
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)      

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.09
                    df_evapo_2041_2070 = df_datos_evapot + 1.98
                    df_evapo_2071_2100 = df_datos_evapot + 2.75


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2011_2040Columna')
                        with open('Ensamble_precipEvapott_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2041_2070Columna')
                        with open('Ensamble_precipEvapott_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2071_2100Columna')
                        with open('Ensamble_precipEvapott_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precipEvapott_2011_2040Columna.txt', 'Ensamble_precipEvapott_2041_2070Columna.txt', 'Ensamble_precipEvapott_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipEvapottColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2011_2040cedex')
                        with open('Ensamble_precipEvapott_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2041_2070cedex')
                        with open('Ensamble_precipEvapott_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2071_2100cedex')
                        with open('Ensamble_precipEvapott_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precipEvapott_2011_2040cedex.txt', 'Ensamble_precipEvapott_2041_2070cedex.txt', 'Ensamble_precipEvapott_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipEvapottcedex.zip", mime="application/zip")

                #Ninguna evapotranspiracion
                elif option1_precip_sup and option3_temp_sup and not option5_evapot:
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    df_precipSup_2011_2040 = df_precipSup * 1.1462
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1612
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1632
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 1.09
                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup + 1.98
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup + 2.75
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2011_2040Columna')
                        with open('Ensamble_precipTemp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2041_2070Columna')
                        with open('Ensamble_precipTemp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2071_2100Columna')
                        with open('Ensamble_precipTemp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precipTemp_2011_2040Columna.txt', 'Ensamble_precipTemp_2041_2070Columna.txt', 'Ensamble_precipTemp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipTempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2011_2040cedex')
                        with open('Ensamble_precipTemp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2041_2070cedex')
                        with open('Ensamble_precipTemp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2071_2100cedex')
                        with open('Ensamble_precipTemp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precipTemp_2011_2040cedex.txt', 'Ensamble_precipTemp_2041_2070cedex.txt', 'Ensamble_precipTemp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipTempcedex.zip", mime="application/zip")


                #Solo temperatura
                elif not option1_precip_sup and option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 1.09

                    df_tempSup_2041_2070 = df_tempSup + 1.98

                    df_tempSup_2071_2100 = df_tempSup + 2.75

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2011_2040Columna')
                        with open('Ensamble_temp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2041_2070Columna')
                        with open('Ensamble_temp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2071_2100Columna')
                        with open('Ensamble_temp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_temp_2011_2040Columna.txt', 'Ensamble_temp_2041_2070Columna.txt', 'Ensamble_temp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_tempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2011_2040cedex')
                        with open('Ensamble_temp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2041_2070cedex')
                        with open('Ensamble_temp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2071_2100cedex')
                        with open('Ensamble_temp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_temp_2011_2040cedex.txt', 'Ensamble_temp_2041_2070cedex.txt', 'Ensamble_temp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_tempcedex.zip", mime="application/zip")

                #Solo precipitación
                elif option1_precip_sup and not option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1462
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1612
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1632
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)  

                    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2011_2040Columna')
                        with open('Ensamble_precip_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2041_2070Columna')
                        with open('Ensamble_precip_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2071_2100Columna')
                        with open('Ensamble_precip_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precip_2011_2040Columna.txt', 'Ensamble_precip_2041_2070Columna.txt', 'Ensamble_precip_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2011_2040cedex')
                        with open('Ensamble_precip_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2041_2070cedex')
                        with open('Ensamble_precip_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2071_2100cedex')
                        with open('Ensamble_precip_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precip_2011_2040cedex.txt', 'Ensamble_precip_2041_2070cedex.txt', 'Ensamble_precip_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipcedex.zip", mime="application/zip")

                #Solo evapotranspiracion
                elif not option1_precip_sup and not option3_temp_sup and  option5_evapot:

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup
                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.09
                    df_evapo_2041_2070 = df_datos_evapot + 1.98
                    df_evapo_2071_2100 = df_datos_evapot + 2.75


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2011_2040Columna')
                        with open('Ensamble_evapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2041_2070Columna')
                        with open('Ensamble_evapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2071_2100Columna')
                        with open('Ensamble_evapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_evapot_2011_2040Columna.txt', 'Ensamble_evapot_2041_2070Columna.txt', 'Ensamble_evapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_evapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2011_2040cedex')
                        with open('Ensamble_evapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2041_2070cedex')
                        with open('Ensamble_evapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2071_2100cedex')
                        with open('Ensamble_evapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_evapot_2011_2040cedex.txt', 'Ensamble_evapot_2041_2070cedex.txt', 'Ensamble_evapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_evapotcedex.zip", mime="application/zip")


                # todos los options
                elif  option1_precip_sup and  option3_temp_sup and  option5_evapot:    
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.09
                    df_evapo_2041_2070 = df_datos_evapot + 1.98
                    df_evapo_2071_2100 = df_datos_evapot + 2.75


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    df_precipSup_2011_2040 = df_precipSup * 1.1462
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1612
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1632
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 1.09
                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                    df_tempSup_2041_2070 = df_tempSup + 1.98
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                    df_tempSup_2071_2100 = df_tempSup + 2.75
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2011_2040Columna')
                        with open('Ensamble_todos_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2041_2070Columna')
                        with open('Ensamble_todos_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2071_2100Columna')
                        with open('Ensamble_todos_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_todos_2011_2040Columna.txt', 'Ensamble_todos_2041_2070Columna.txt', 'Ensamble_todos_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_todosColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2011_2040cedex')
                        with open('Ensamble_todos_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2041_2070cedex')
                        with open('Ensamble_todos_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2071_2100cedex')
                        with open('Ensamble_todos_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_todos_2011_2040cedex.txt', 'Ensamble_todos_2041_2070cedex.txt', 'Ensamble_todos_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_todoscedex.zip", mime="application/zip")



        #trimestre
        elif option7_anu_tri == 'Trimestral':
            if option8_RCP == '2.6':
                #Ninguna precipitacion
                if not option1_precip_sup and option3_temp_sup and option5_evapot:
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)


                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)


                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_tempEvapot_2011_2040Columna')
                        with open('trimestre_2_6_tempEvapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_tempEvapot_2041_2070Columna')
                        with open('trimestre_2_6_tempEvapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_tempEvapot_2071_2100Columna')
                        with open('trimestre_2_6_tempEvapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_tempEvapot_2011_2040Columna.txt', 'trimestre_2_6_tempEvapot_2041_2070Columna.txt', 'trimestre_2_6_tempEvapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_tempEvapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_tempEvapot_2011_2040cedex')
                        with open('trimestre_2_6_tempEvapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_tempEvapot_2041_2070cedex')
                        with open('trimestre_2_6_tempEvapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_tempEvapot_2071_2100cedex')
                        with open('trimestre_2_6_tempEvapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_tempEvapot_2011_2040cedex.txt', 'trimestre_2_6_tempEvapot_2041_2070cedex.txt', 'trimestre_2_6_tempEvapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_tempEvapotcedex.zip", mime="application/zip")

                #Ninguna temperatura
                elif option1_precip_sup and not option3_temp_sup and option5_evapot:    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipEvapott_2011_2040Columna')
                        with open('trimestre_2_6_precipEvapott_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipEvapott_2041_2070Columna')
                        with open('trimestre_2_6_precipEvapott_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipEvapott_2071_2100Columna')
                        with open('trimestre_2_6_precipEvapott_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_precipEvapott_2011_2040Columna.txt', 'trimestre_2_6_precipEvapott_2041_2070Columna.txt', 'trimestre_2_6_precipEvapott_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_precipEvapottColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipEvapott_2011_2040cedex')
                        with open('trimestre_2_6_precipEvapott_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipEvapott_2041_2070cedex')
                        with open('trimestre_2_6_precipEvapott_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipEvapott_2071_2100cedex')
                        with open('trimestre_2_6_precipEvapott_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_precipEvapott_2011_2040cedex.txt', 'trimestre_2_6_precipEvapott_2041_2070cedex.txt', 'trimestre_2_6_precipEvapott_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_precipEvapottcedex.zip", mime="application/zip")

                #Ninguna evapotranspiracion
                elif option1_precip_sup and option3_temp_sup and not option5_evapot:
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipTemp_2011_2040Columna')
                        with open('trimestre_2_6_precipTemp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipTemp_2041_2070Columna')
                        with open('trimestre_2_6_precipTemp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipTemp_2071_2100Columna')
                        with open('trimestre_2_6_precipTemp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_precipTemp_2011_2040Columna.txt', 'trimestre_2_6_precipTemp_2041_2070Columna.txt', 'trimestre_2_6_precipTemp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_precipTempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipTemp_2011_2040cedex')
                        with open('trimestre_2_6_precipTemp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipTemp_2041_2070cedex')
                        with open('trimestre_2_6_precipTemp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precipTemp_2071_2100cedex')
                        with open('trimestre_2_6_precipTemp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_precipTemp_2011_2040cedex.txt', 'trimestre_2_6_precipTemp_2041_2070cedex.txt', 'trimestre_2_6_precipTemp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_precipTempcedex.zip", mime="application/zip")


                #Solo temperatura
                elif not option1_precip_sup and option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_temp_2011_2040Columna')
                        with open('trimestre_2_6_temp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_temp_2041_2070Columna')
                        with open('trimestre_2_6_temp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_temp_2071_2100Columna')
                        with open('trimestre_2_6_temp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_temp_2011_2040Columna.txt', 'trimestre_2_6_temp_2041_2070Columna.txt', 'trimestre_2_6_temp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_tempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_temp_2011_2040cedex')
                        with open('trimestre_2_6_temp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_temp_2041_2070cedex')
                        with open('trimestre_2_6_temp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_temp_2071_2100cedex')
                        with open('trimestre_2_6_temp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_temp_2011_2040cedex.txt', 'trimestre_2_6_temp_2041_2070cedex.txt', 'trimestre_2_6_temp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_tempcedex.zip", mime="application/zip")

                #Solo precipitación
                elif option1_precip_sup and not option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precip_2011_2040Columna')
                        with open('trimestre_2_6_precip_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precip_2041_2070Columna')
                        with open('trimestre_2_6_precip_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precip_2071_2100Columna')
                        with open('trimestre_2_6_precip_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_precip_2011_2040Columna.txt', 'trimestre_2_6_precip_2041_2070Columna.txt', 'trimestre_2_6_precip_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_precipColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precip_2011_2040cedex')
                        with open('trimestre_2_6_precip_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precip_2041_2070cedex')
                        with open('trimestre_2_6_precip_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_precip_2071_2100cedex')
                        with open('trimestre_2_6_precip_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_precip_2011_2040cedex.txt', 'trimestre_2_6_precip_2041_2070cedex.txt', 'trimestre_2_6_precip_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_precipcedex.zip", mime="application/zip")

                #Solo evapotranspiracion
                elif not option1_precip_sup and not option3_temp_sup and  option5_evapot:

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup
                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)

                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)      
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_evapot_2011_2040Columna')
                        with open('trimestre_2_6_evapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_evapot_2041_2070Columna')
                        with open('trimestre_2_6_evapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_evapot_2071_2100Columna')
                        with open('trimestre_2_6_evapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_evapot_2011_2040Columna.txt', 'trimestre_2_6_evapot_2041_2070Columna.txt', 'trimestre_2_6_evapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_evapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_evapot_2011_2040cedex')
                        with open('trimestre_2_6_evapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_evapot_2041_2070cedex')
                        with open('trimestre_2_6_evapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_evapot_2071_2100cedex')
                        with open('trimestre_2_6_evapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_evapot_2011_2040cedex.txt', 'trimestre_2_6_evapot_2041_2070cedex.txt', 'trimestre_2_6_evapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_evapotcedex.zip", mime="application/zip")


                # todos los options
                elif  option1_precip_sup and  option3_temp_sup and  option5_evapot: 
                   
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP) 


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)


                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)                                                    

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_todos_2011_2040Columna')
                        with open('trimestre_2_6_todos_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_todos_2041_2070Columna')
                        with open('trimestre_2_6_todos_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_todos_2071_2100Columna')
                        with open('trimestre_2_6_todos_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_todos_2011_2040Columna.txt', 'trimestre_2_6_todos_2041_2070Columna.txt', 'trimestre_2_6_todos_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_todosColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_todos_2011_2040cedex')
                        with open('trimestre_2_6_todos_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_todos_2041_2070cedex')
                        with open('trimestre_2_6_todos_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_2_6_todos_2071_2100cedex')
                        with open('trimestre_2_6_todos_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_2_6_todos_2011_2040cedex.txt', 'trimestre_2_6_todos_2041_2070cedex.txt', 'trimestre_2_6_todos_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_2_6_todoscedex.zip", mime="application/zip")

            elif option8_RCP == '4.5':
                #Ninguna precipitacion
                if not option1_precip_sup and option3_temp_sup and option5_evapot:
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)


                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)


                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_tempEvapot_2011_2040Columna')
                        with open('trimestre_4_5_tempEvapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_tempEvapot_2041_2070Columna')
                        with open('trimestre_4_5_tempEvapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_tempEvapot_2071_2100Columna')
                        with open('trimestre_4_5_tempEvapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_tempEvapot_2011_2040Columna.txt', 'trimestre_4_5_tempEvapot_2041_2070Columna.txt', 'trimestre_4_5_tempEvapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_tempEvapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_tempEvapot_2011_2040cedex')
                        with open('trimestre_4_5_tempEvapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_tempEvapot_2041_2070cedex')
                        with open('trimestre_4_5_tempEvapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_tempEvapot_2071_2100cedex')
                        with open('trimestre_4_5_tempEvapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_tempEvapot_2011_2040cedex.txt', 'trimestre_4_5_tempEvapot_2041_2070cedex.txt', 'trimestre_4_5_tempEvapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_tempEvapotcedex.zip", mime="application/zip")

                #Ninguna temperatura
                elif option1_precip_sup and not option3_temp_sup and option5_evapot:    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipEvapott_2011_2040Columna')
                        with open('trimestre_4_5_precipEvapott_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipEvapott_2041_2070Columna')
                        with open('trimestre_4_5_precipEvapott_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipEvapott_2071_2100Columna')
                        with open('trimestre_4_5_precipEvapott_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_precipEvapott_2011_2040Columna.txt', 'trimestre_4_5_precipEvapott_2041_2070Columna.txt', 'trimestre_4_5_precipEvapott_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_precipEvapottColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipEvapott_2011_2040cedex')
                        with open('trimestre_4_5_precipEvapott_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipEvapott_2041_2070cedex')
                        with open('trimestre_4_5_precipEvapott_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipEvapott_2071_2100cedex')
                        with open('trimestre_4_5_precipEvapott_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_precipEvapott_2011_2040cedex.txt', 'trimestre_4_5_precipEvapott_2041_2070cedex.txt', 'trimestre_4_5_precipEvapott_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_precipEvapottcedex.zip", mime="application/zip")

                #Ninguna evapotranspiracion
                elif option1_precip_sup and option3_temp_sup and not option5_evapot:
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipTemp_2011_2040Columna')
                        with open('trimestre_4_5_precipTemp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipTemp_2041_2070Columna')
                        with open('trimestre_4_5_precipTemp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipTemp_2071_2100Columna')
                        with open('trimestre_4_5_precipTemp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_precipTemp_2011_2040Columna.txt', 'trimestre_4_5_precipTemp_2041_2070Columna.txt', 'trimestre_4_5_precipTemp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_precipTempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipTemp_2011_2040cedex')
                        with open('trimestre_4_5_precipTemp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipTemp_2041_2070cedex')
                        with open('trimestre_4_5_precipTemp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precipTemp_2071_2100cedex')
                        with open('trimestre_4_5_precipTemp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_precipTemp_2011_2040cedex.txt', 'trimestre_4_5_precipTemp_2041_2070cedex.txt', 'trimestre_4_5_precipTemp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_precipTempcedex.zip", mime="application/zip")


                #Solo temperatura
                elif not option1_precip_sup and option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_temp_2011_2040Columna')
                        with open('trimestre_4_5_temp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_temp_2041_2070Columna')
                        with open('trimestre_4_5_temp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_temp_2071_2100Columna')
                        with open('trimestre_4_5_temp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_temp_2011_2040Columna.txt', 'trimestre_4_5_temp_2041_2070Columna.txt', 'trimestre_4_5_temp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_tempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_temp_2011_2040cedex')
                        with open('trimestre_4_5_temp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_temp_2041_2070cedex')
                        with open('trimestre_4_5_temp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_temp_2071_2100cedex')
                        with open('trimestre_4_5_temp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_temp_2011_2040cedex.txt', 'trimestre_4_5_temp_2041_2070cedex.txt', 'trimestre_4_5_temp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_tempcedex.zip", mime="application/zip")

                #Solo precipitación
                elif option1_precip_sup and not option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precip_2011_2040Columna')
                        with open('trimestre_4_5_precip_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precip_2041_2070Columna')
                        with open('trimestre_4_5_precip_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precip_2071_2100Columna')
                        with open('trimestre_4_5_precip_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_precip_2011_2040Columna.txt', 'trimestre_4_5_precip_2041_2070Columna.txt', 'trimestre_4_5_precip_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_precipColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precip_2011_2040cedex')
                        with open('trimestre_4_5_precip_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precip_2041_2070cedex')
                        with open('trimestre_4_5_precip_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_precip_2071_2100cedex')
                        with open('trimestre_4_5_precip_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_precip_2011_2040cedex.txt', 'trimestre_4_5_precip_2041_2070cedex.txt', 'trimestre_4_5_precip_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_precipcedex.zip", mime="application/zip")

                #Solo evapotranspiracion
                elif not option1_precip_sup and not option3_temp_sup and  option5_evapot:

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup
                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)

                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)      
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_evapot_2011_2040Columna')
                        with open('trimestre_4_5_evapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_evapot_2041_2070Columna')
                        with open('trimestre_4_5_evapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_evapot_2071_2100Columna')
                        with open('trimestre_4_5_evapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_evapot_2011_2040Columna.txt', 'trimestre_4_5_evapot_2041_2070Columna.txt', 'trimestre_4_5_evapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_evapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_evapot_2011_2040cedex')
                        with open('trimestre_4_5_evapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_evapot_2041_2070cedex')
                        with open('trimestre_4_5_evapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_evapot_2071_2100cedex')
                        with open('trimestre_4_5_evapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_evapot_2011_2040cedex.txt', 'trimestre_4_5_evapot_2041_2070cedex.txt', 'trimestre_4_5_evapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_evapotcedex.zip", mime="application/zip")


                # todos los options
                elif  option1_precip_sup and  option3_temp_sup and  option5_evapot: 
                   
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)



                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)


                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)                                                    

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_todos_2011_2040Columna')
                        with open('trimestre_4_5_todos_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_todos_2041_2070Columna')
                        with open('trimestre_4_5_todos_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_todos_2071_2100Columna')
                        with open('trimestre_4_5_todos_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_todos_2011_2040Columna.txt', 'trimestre_4_5_todos_2041_2070Columna.txt', 'trimestre_4_5_todos_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_todosColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_todos_2011_2040cedex')
                        with open('trimestre_4_5_todos_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_todos_2041_2070cedex')
                        with open('trimestre_4_5_todos_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_4_5_todos_2071_2100cedex')
                        with open('trimestre_4_5_todos_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_4_5_todos_2011_2040cedex.txt', 'trimestre_4_5_todos_2041_2070cedex.txt', 'trimestre_4_5_todos_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_4_5_todoscedex.zip", mime="application/zip")


            elif option8_RCP == '6.0':
                #Ninguna precipitacion
                if not option1_precip_sup and option3_temp_sup and option5_evapot:
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)


                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)


                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_tempEvapot_2011_2040Columna')
                        with open('trimestre_6_0_tempEvapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_tempEvapot_2041_2070Columna')
                        with open('trimestre_6_0_tempEvapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_tempEvapot_2071_2100Columna')
                        with open('trimestre_6_0_tempEvapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_tempEvapot_2011_2040Columna.txt', 'trimestre_6_0_tempEvapot_2041_2070Columna.txt', 'trimestre_6_0_tempEvapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_tempEvapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_tempEvapot_2011_2040cedex')
                        with open('trimestre_6_0_tempEvapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_tempEvapot_2041_2070cedex')
                        with open('trimestre_6_0_tempEvapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_tempEvapot_2071_2100cedex')
                        with open('trimestre_6_0_tempEvapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_tempEvapot_2011_2040cedex.txt', 'trimestre_6_0_tempEvapot_2041_2070cedex.txt', 'trimestre_6_0_tempEvapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_tempEvapotcedex.zip", mime="application/zip")

                #Ninguna temperatura
                elif option1_precip_sup and not option3_temp_sup and option5_evapot:    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipEvapott_2011_2040Columna')
                        with open('trimestre_6_0_precipEvapott_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipEvapott_2041_2070Columna')
                        with open('trimestre_6_0_precipEvapott_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipEvapott_2071_2100Columna')
                        with open('trimestre_6_0_precipEvapott_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_precipEvapott_2011_2040Columna.txt', 'trimestre_6_0_precipEvapott_2041_2070Columna.txt', 'trimestre_6_0_precipEvapott_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_precipEvapottColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipEvapott_2011_2040cedex')
                        with open('trimestre_6_0_precipEvapott_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipEvapott_2041_2070cedex')
                        with open('trimestre_6_0_precipEvapott_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipEvapott_2071_2100cedex')
                        with open('trimestre_6_0_precipEvapott_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_precipEvapott_2011_2040cedex.txt', 'trimestre_6_0_precipEvapott_2041_2070cedex.txt', 'trimestre_6_0_precipEvapott_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_precipEvapottcedex.zip", mime="application/zip")

                #Ninguna evapotranspiracion
                elif option1_precip_sup and option3_temp_sup and not option5_evapot:
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipTemp_2011_2040Columna')
                        with open('trimestre_6_0_precipTemp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipTemp_2041_2070Columna')
                        with open('trimestre_6_0_precipTemp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipTemp_2071_2100Columna')
                        with open('trimestre_6_0_precipTemp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_precipTemp_2011_2040Columna.txt', 'trimestre_6_0_precipTemp_2041_2070Columna.txt', 'trimestre_6_0_precipTemp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_precipTempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipTemp_2011_2040cedex')
                        with open('trimestre_6_0_precipTemp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipTemp_2041_2070cedex')
                        with open('trimestre_6_0_precipTemp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precipTemp_2071_2100cedex')
                        with open('trimestre_6_0_precipTemp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_precipTemp_2011_2040cedex.txt', 'trimestre_6_0_precipTemp_2041_2070cedex.txt', 'trimestre_6_0_precipTemp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_precipTempcedex.zip", mime="application/zip")


                #Solo temperatura
                elif not option1_precip_sup and option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_temp_2011_2040Columna')
                        with open('trimestre_6_0_temp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_temp_2041_2070Columna')
                        with open('trimestre_6_0_temp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_temp_2071_2100Columna')
                        with open('trimestre_6_0_temp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_temp_2011_2040Columna.txt', 'trimestre_6_0_temp_2041_2070Columna.txt', 'trimestre_6_0_temp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_tempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_temp_2011_2040cedex')
                        with open('trimestre_6_0_temp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_temp_2041_2070cedex')
                        with open('trimestre_6_0_temp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_temp_2071_2100cedex')
                        with open('trimestre_6_0_temp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_temp_2011_2040cedex.txt', 'trimestre_6_0_temp_2041_2070cedex.txt', 'trimestre_6_0_temp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_tempcedex.zip", mime="application/zip")

                #Solo precipitación
                elif option1_precip_sup and not option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precip_2011_2040Columna')
                        with open('trimestre_6_0_precip_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precip_2041_2070Columna')
                        with open('trimestre_6_0_precip_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precip_2071_2100Columna')
                        with open('trimestre_6_0_precip_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_precip_2011_2040Columna.txt', 'trimestre_6_0_precip_2041_2070Columna.txt', 'trimestre_6_0_precip_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_precipColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precip_2011_2040cedex')
                        with open('trimestre_6_0_precip_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precip_2041_2070cedex')
                        with open('trimestre_6_0_precip_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_precip_2071_2100cedex')
                        with open('trimestre_6_0_precip_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_precip_2011_2040cedex.txt', 'trimestre_6_0_precip_2041_2070cedex.txt', 'trimestre_6_0_precip_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_precipcedex.zip", mime="application/zip")

                #Solo evapotranspiracion
                elif not option1_precip_sup and not option3_temp_sup and  option5_evapot:

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup
                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)

                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)      
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_evapot_2011_2040Columna')
                        with open('trimestre_6_0_evapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_evapot_2041_2070Columna')
                        with open('trimestre_6_0_evapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_evapot_2071_2100Columna')
                        with open('trimestre_6_0_evapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_evapot_2011_2040Columna.txt', 'trimestre_6_0_evapot_2041_2070Columna.txt', 'trimestre_6_0_evapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_evapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_evapot_2011_2040cedex')
                        with open('trimestre_6_0_evapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_evapot_2041_2070cedex')
                        with open('trimestre_6_0_evapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_evapot_2071_2100cedex')
                        with open('trimestre_6_0_evapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_evapot_2011_2040cedex.txt', 'trimestre_6_0_evapot_2041_2070cedex.txt', 'trimestre_6_0_evapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_evapotcedex.zip", mime="application/zip")


                # todos los options
                elif  option1_precip_sup and  option3_temp_sup and  option5_evapot: 
                   
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)


                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)                                                    

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_todos_2011_2040Columna')
                        with open('trimestre_6_0_todos_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_todos_2041_2070Columna')
                        with open('trimestre_6_0_todos_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_todos_2071_2100Columna')
                        with open('trimestre_6_0_todos_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_todos_2011_2040Columna.txt', 'trimestre_6_0_todos_2041_2070Columna.txt', 'trimestre_6_0_todos_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_todosColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_todos_2011_2040cedex')
                        with open('trimestre_6_0_todos_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_todos_2041_2070cedex')
                        with open('trimestre_6_0_todos_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_6_0_todos_2071_2100cedex')
                        with open('trimestre_6_0_todos_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_6_0_todos_2011_2040cedex.txt', 'trimestre_6_0_todos_2041_2070cedex.txt', 'trimestre_6_0_todos_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_6_0_todoscedex.zip", mime="application/zip")


            elif option8_RCP == '8.5':
                #Ninguna precipitacion
                if not option1_precip_sup and option3_temp_sup and option5_evapot:
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)


                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)


                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_tempEvapot_2011_2040Columna')
                        with open('trimestre_8_5_tempEvapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_tempEvapot_2041_2070Columna')
                        with open('trimestre_8_5_tempEvapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_tempEvapot_2071_2100Columna')
                        with open('trimestre_8_5_tempEvapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_tempEvapot_2011_2040Columna.txt', 'trimestre_8_5_tempEvapot_2041_2070Columna.txt', 'trimestre_8_5_tempEvapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_tempEvapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_tempEvapot_2011_2040cedex')
                        with open('trimestre_8_5_tempEvapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_tempEvapot_2041_2070cedex')
                        with open('trimestre_8_5_tempEvapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_tempEvapot_2071_2100cedex')
                        with open('trimestre_8_5_tempEvapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_tempEvapot_2011_2040cedex.txt', 'trimestre_8_5_tempEvapot_2041_2070cedex.txt', 'trimestre_8_5_tempEvapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_tempEvapotcedex.zip", mime="application/zip")

                #Ninguna temperatura
                elif option1_precip_sup and not option3_temp_sup and option5_evapot:    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipEvapott_2011_2040Columna')
                        with open('trimestre_8_5_precipEvapott_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipEvapott_2041_2070Columna')
                        with open('trimestre_8_5_precipEvapott_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipEvapott_2071_2100Columna')
                        with open('trimestre_8_5_precipEvapott_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_precipEvapott_2011_2040Columna.txt', 'trimestre_8_5_precipEvapott_2041_2070Columna.txt', 'trimestre_8_5_precipEvapott_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_precipEvapottColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipEvapott_2011_2040cedex')
                        with open('trimestre_8_5_precipEvapott_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipEvapott_2041_2070cedex')
                        with open('trimestre_8_5_precipEvapott_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipEvapott_2071_2100cedex')
                        with open('trimestre_8_5_precipEvapott_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_precipEvapott_2011_2040cedex.txt', 'trimestre_8_5_precipEvapott_2041_2070cedex.txt', 'trimestre_8_5_precipEvapott_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_precipEvapottcedex.zip", mime="application/zip")

                #Ninguna evapotranspiracion
                elif option1_precip_sup and option3_temp_sup and not option5_evapot:
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipTemp_2011_2040Columna')
                        with open('trimestre_8_5_precipTemp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipTemp_2041_2070Columna')
                        with open('trimestre_8_5_precipTemp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipTemp_2071_2100Columna')
                        with open('trimestre_8_5_precipTemp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_precipTemp_2011_2040Columna.txt', 'trimestre_8_5_precipTemp_2041_2070Columna.txt', 'trimestre_8_5_precipTemp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_precipTempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipTemp_2011_2040cedex')
                        with open('trimestre_8_5_precipTemp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipTemp_2041_2070cedex')
                        with open('trimestre_8_5_precipTemp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precipTemp_2071_2100cedex')
                        with open('trimestre_8_5_precipTemp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_precipTemp_2011_2040cedex.txt', 'trimestre_8_5_precipTemp_2041_2070cedex.txt', 'trimestre_8_5_precipTemp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_precipTempcedex.zip", mime="application/zip")


                #Solo temperatura
                elif not option1_precip_sup and option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_temp_2011_2040Columna')
                        with open('trimestre_8_5_temp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_temp_2041_2070Columna')
                        with open('trimestre_8_5_temp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_temp_2071_2100Columna')
                        with open('trimestre_8_5_temp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_temp_2011_2040Columna.txt', 'trimestre_8_5_temp_2041_2070Columna.txt', 'trimestre_8_5_temp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_tempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_temp_2011_2040cedex')
                        with open('trimestre_8_5_temp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_temp_2041_2070cedex')
                        with open('trimestre_8_5_temp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_temp_2071_2100cedex')
                        with open('trimestre_8_5_temp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_temp_2011_2040cedex.txt', 'trimestre_8_5_temp_2041_2070cedex.txt', 'trimestre_8_5_temp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_tempcedex.zip", mime="application/zip")

                #Solo precipitación
                elif option1_precip_sup and not option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precip_2011_2040Columna')
                        with open('trimestre_8_5_precip_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precip_2041_2070Columna')
                        with open('trimestre_8_5_precip_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precip_2071_2100Columna')
                        with open('trimestre_8_5_precip_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_precip_2011_2040Columna.txt', 'trimestre_8_5_precip_2041_2070Columna.txt', 'trimestre_8_5_precip_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_precipColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precip_2011_2040cedex')
                        with open('trimestre_8_5_precip_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precip_2041_2070cedex')
                        with open('trimestre_8_5_precip_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_precip_2071_2100cedex')
                        with open('trimestre_8_5_precip_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_precip_2011_2040cedex.txt', 'trimestre_8_5_precip_2041_2070cedex.txt', 'trimestre_8_5_precip_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_precipcedex.zip", mime="application/zip")

                #Solo evapotranspiracion
                elif not option1_precip_sup and not option3_temp_sup and  option5_evapot:

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup
                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)
                    df_ub2 = df_ub.set_index('CODIGO')

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)

                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)      
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_evapot_2011_2040Columna')
                        with open('trimestre_8_5_evapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_evapot_2041_2070Columna')
                        with open('trimestre_8_5_evapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_evapot_2071_2100Columna')
                        with open('trimestre_8_5_evapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_evapot_2011_2040Columna.txt', 'trimestre_8_5_evapot_2041_2070Columna.txt', 'trimestre_8_5_evapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_evapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_evapot_2011_2040cedex')
                        with open('trimestre_8_5_evapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_evapot_2041_2070cedex')
                        with open('trimestre_8_5_evapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_evapot_2071_2100cedex')
                        with open('trimestre_8_5_evapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_evapot_2011_2040cedex.txt', 'trimestre_8_5_evapot_2041_2070cedex.txt', 'trimestre_8_5_evapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_evapotcedex.zip", mime="application/zip")


                # todos los options
                elif  option1_precip_sup and  option3_temp_sup and  option5_evapot: 
                   
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    (df_evapo_2011_2040, df_evapo_2041_2070, df_evapo_2071_2100) = trimestre_temp(df_datos_evapot, option8_RCP)


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)


                    (df_precipSup_2011_2040, df_precipSup_2041_2070, df_precipSup_2071_2100) = trimestre_precip(df_precipSup, option8_RCP)

                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)                                                    

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    (df_tempSup_2011_2040, df_tempSup_2041_2070, df_tempSup_2071_2100) = trimestre_temp(df_tempSup, option8_RCP)

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_todos_2011_2040Columna')
                        with open('trimestre_8_5_todos_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_todos_2041_2070Columna')
                        with open('trimestre_8_5_todos_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_todos_2071_2100Columna')
                        with open('trimestre_8_5_todos_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_todos_2011_2040Columna.txt', 'trimestre_8_5_todos_2041_2070Columna.txt', 'trimestre_8_5_todos_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_todosColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_todos_2011_2040cedex')
                        with open('trimestre_8_5_todos_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_todos_2041_2070cedex')
                        with open('trimestre_8_5_todos_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'trimestre_8_5_todos_2071_2100cedex')
                        with open('trimestre_8_5_todos_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['trimestre_8_5_todos_2011_2040cedex.txt', 'trimestre_8_5_todos_2041_2070cedex.txt', 'trimestre_8_5_todos_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="trimestre_8_5_todoscedex.zip", mime="application/zip")


            #trimestre
            elif option8_RCP == 'Ensamble':
                



                #Ninguna precipitacion
                if not option1_precip_sup and option3_temp_sup and option5_evapot:
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_ub2 = df_ub.set_index('CODIGO')

                    df_tempSup_2011_2040 = df_tempSup + 1.09

                    df_tempSup_2041_2070 = df_tempSup + 1.98

                    df_tempSup_2071_2100 = df_tempSup + 2.75

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.09
                    df_evapo_2041_2070 = df_datos_evapot + 1.98
                    df_evapo_2071_2100 = df_datos_evapot + 2.75
                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  


                                #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2011_2040Columna')
                        with open('Ensamble_tempEvapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2041_2070Columna')
                        with open('Ensamble_tempEvapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2071_2100Columna')
                        with open('Ensamble_tempEvapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_tempEvapot_2011_2040Columna.txt', 'Ensamble_tempEvapot_2041_2070Columna.txt', 'Ensamble_tempEvapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_tempEvapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2011_2040cedex')
                        with open('Ensamble_tempEvapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2041_2070cedex')
                        with open('Ensamble_tempEvapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_tempEvapot_2071_2100cedex')
                        with open('Ensamble_tempEvapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_tempEvapot_2011_2040cedex.txt', 'Ensamble_tempEvapot_2041_2070cedex.txt', 'Ensamble_tempEvapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_tempEvapotcedex.zip", mime="application/zip")

                #Ninguna temperatura
                elif option1_precip_sup and not option3_temp_sup and option5_evapot:    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1462
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1612
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1632
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)      

                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.09
                    df_evapo_2041_2070 = df_datos_evapot + 1.98
                    df_evapo_2071_2100 = df_datos_evapot + 2.75


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2011_2040Columna')
                        with open('Ensamble_precipEvapott_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2041_2070Columna')
                        with open('Ensamble_precipEvapott_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2071_2100Columna')
                        with open('Ensamble_precipEvapott_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precipEvapott_2011_2040Columna.txt', 'Ensamble_precipEvapott_2041_2070Columna.txt', 'Ensamble_precipEvapott_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipEvapottColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2011_2040cedex')
                        with open('Ensamble_precipEvapott_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2041_2070cedex')
                        with open('Ensamble_precipEvapott_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipEvapott_2071_2100cedex')
                        with open('Ensamble_precipEvapott_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precipEvapott_2011_2040cedex.txt', 'Ensamble_precipEvapott_2041_2070cedex.txt', 'Ensamble_precipEvapott_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipEvapottcedex.zip", mime="application/zip")

                #Ninguna evapotranspiracion
                elif option1_precip_sup and option3_temp_sup and not option5_evapot:
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    df_precipSup_2011_2040 = df_precipSup * 1.1462
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-1) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1612
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-1) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1632
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-1)   

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 1.09
                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup + 1.98
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup + 2.75
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2011_2040Columna')
                        with open('Ensamble_precipTemp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2041_2070Columna')
                        with open('Ensamble_precipTemp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2071_2100Columna')
                        with open('Ensamble_precipTemp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precipTemp_2011_2040Columna.txt', 'Ensamble_precipTemp_2041_2070Columna.txt', 'Ensamble_precipTemp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipTempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2011_2040cedex')
                        with open('Ensamble_precipTemp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2041_2070cedex')
                        with open('Ensamble_precipTemp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precipTemp_2071_2100cedex')
                        with open('Ensamble_precipTemp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precipTemp_2011_2040cedex.txt', 'Ensamble_precipTemp_2041_2070cedex.txt', 'Ensamble_precipTemp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipTempcedex.zip", mime="application/zip")


                #Solo temperatura
                elif not option1_precip_sup and option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  

                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 1.09

                    df_tempSup_2041_2070 = df_tempSup + 1.98

                    df_tempSup_2071_2100 = df_tempSup + 2.75

                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-99) 

                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-99) 

                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-99) 

                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2011_2040Columna')
                        with open('Ensamble_temp_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2041_2070Columna')
                        with open('Ensamble_temp_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2071_2100Columna')
                        with open('Ensamble_temp_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_temp_2011_2040Columna.txt', 'Ensamble_temp_2041_2070Columna.txt', 'Ensamble_temp_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_tempColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup_2011_2040, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2011_2040cedex')
                        with open('Ensamble_temp_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup_2041_2070, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2041_2070cedex')
                        with open('Ensamble_temp_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup_2071_2100, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_temp_2071_2100cedex')
                        with open('Ensamble_temp_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_temp_2011_2040cedex.txt', 'Ensamble_temp_2041_2070cedex.txt', 'Ensamble_temp_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_tempcedex.zip", mime="application/zip")

                #Solo precipitación
                elif option1_precip_sup and not option3_temp_sup and not option5_evapot:
                    option5_evapot = 'None'
                    df_datos_evapot = option5_evapot

                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup

                    df_precipSup_2011_2040 = df_precipSup * 1.1462
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1612
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1632
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)  

                    
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2011_2040Columna')
                        with open('Ensamble_precip_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2041_2070Columna')
                        with open('Ensamble_precip_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2071_2100Columna')
                        with open('Ensamble_precip_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precip_2011_2040Columna.txt', 'Ensamble_precip_2041_2070Columna.txt', 'Ensamble_precip_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2011_2040cedex')
                        with open('Ensamble_precip_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2041_2070cedex')
                        with open('Ensamble_precip_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup, df_datos_evapot, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_precip_2071_2100cedex')
                        with open('Ensamble_precip_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_precip_2011_2040cedex.txt', 'Ensamble_precip_2041_2070cedex.txt', 'Ensamble_precip_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_precipcedex.zip", mime="application/zip")

                #Solo evapotranspiracion
                elif not option1_precip_sup and not option3_temp_sup and  option5_evapot:

                    option3_temp_sup = 'None'
                    df_tempSup = option3_temp_sup
                    option1_precip_sup = 'None'
                    df_precipSup = option1_precip_sup  
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.09
                    df_evapo_2041_2070 = df_datos_evapot + 1.98
                    df_evapo_2071_2100 = df_datos_evapot + 2.75


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                        #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇

                        arch_columna = archivoEvento(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2011_2040Columna')
                        with open('Ensamble_evapot_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2041_2070Columna')
                        with open('Ensamble_evapot_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2071_2100Columna')
                        with open('Ensamble_evapot_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_evapot_2011_2040Columna.txt', 'Ensamble_evapot_2041_2070Columna.txt', 'Ensamble_evapot_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_evapotColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup, df_tempSup, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2011_2040cedex')
                        with open('Ensamble_evapot_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2041_2070cedex')
                        with open('Ensamble_evapot_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup,  df_tempSup, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_evapot_2071_2100cedex')
                        with open('Ensamble_evapot_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_evapot_2011_2040cedex.txt', 'Ensamble_evapot_2041_2070cedex.txt', 'Ensamble_evapot_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_evapotcedex.zip", mime="application/zip")


                # todos los options
                elif  option1_precip_sup and  option3_temp_sup and  option5_evapot:    
                    #----------------Evapotranspiracion--------------------
                    df_datos_evapot = abrirArchivos(rutaT, "T", option5_evapot)

                    df_evapo_2011_2040 = df_datos_evapot + 1.09
                    df_evapo_2041_2070 = df_datos_evapot + 1.98
                    df_evapo_2071_2100 = df_datos_evapot + 2.75


                    df_evapot_2011_2040 = calcEvapotranspiracion(df_evapo_2011_2040, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2041_2070 = calcEvapotranspiracion(df_evapo_2041_2070, df_ub2, df_radiacion, option5_evapot)
                    df_evapot_2071_2100 = calcEvapotranspiracion(df_evapo_2071_2100, df_ub2, df_radiacion, option5_evapot)    
                    #--------------------------Lectura datos de precipitación-------------------------------------
                    df_precipSup = abrirArchivos(rutaP, "P", option1_precip_sup)

                    df_precipSup_2011_2040 = df_precipSup * 1.1462
                    df_precipSup_2011_2040 = df_precipSup_2011_2040.fillna(-99) 

                    df_precipSup_2041_2070 = df_precipSup * 1.1612
                    df_precipSup_2041_2070 = df_precipSup_2041_2070.fillna(-99) 

                    df_precipSup_2071_2100 = df_precipSup * 1.1632
                    df_precipSup_2071_2100 = df_precipSup_2071_2100.fillna(-99)   
                    #--------------------------Lectura datos de temperatura---------------------------------------
                    df_tempSup = abrirArchivos(rutaT, "T", option3_temp_sup)
                    df_tempSup_2011_2040 = df_tempSup + 1.09
                    df_tempSup_2011_2040 = df_tempSup_2011_2040.fillna(-1) 

                    df_tempSup_2041_2070 = df_tempSup + 1.98
                    df_tempSup_2041_2070 = df_tempSup_2041_2070.fillna(-1) 

                    df_tempSup_2071_2100 = df_tempSup + 2.75
                    df_tempSup_2071_2100 = df_tempSup_2071_2100.fillna(-1)   
                    #--------------------------------Generar archivo Tetis-----------------------------------------------
                    if 'Columna' in option9_cedex_col: # If user selects Columna  do 👇


                        
                        arch_columna = archivoEvento(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2011_2040Columna')
                        with open('Ensamble_todos_2011_2040Columna.txt', 'r') as f:
                            arch_columna2 = f.read()
                        f.close()

                    
                        arch_columna3 = archivoEvento(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2041_2070Columna')
                        with open('Ensamble_todos_2041_2070Columna.txt', 'r') as f:
                            arch_columna4 = f.read()
                        f.close()

                    
                        arch_columna5 = archivoEvento(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2071_2100Columna')
                        with open('Ensamble_todos_2071_2100Columna.txt', 'r') as f:
                            arch_columna6 = f.read()
                        f.close()


                        file_paths =['Ensamble_todos_2011_2040Columna.txt', 'Ensamble_todos_2041_2070Columna.txt', 'Ensamble_todos_2071_2100Columna.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_todosColumna.zip", mime="application/zip")



                    if 'Cedex' in option9_cedex_col: # If user selects Cedex  do 👇

                        
                        arch_cedex = archivoCEDEX(df_precipSup_2011_2040, df_tempSup_2011_2040, df_evapot_2011_2040, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2011_2040cedex')
                        with open('Ensamble_todos_2011_2040cedex.txt', 'r') as f:
                            arch_cedex2 = f.read()
                        f.close()

                    
                        arch_cedex3 = archivoCEDEX(df_precipSup_2041_2070,  df_tempSup_2041_2070, df_evapot_2041_2070, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2041_2070cedex')
                        with open('Ensamble_todos_2041_2070cedex.txt', 'r') as f:
                            arch_cedex4 = f.read()
                        f.close()

                    
                        arch_cedex5 = archivoCEDEX(df_precipSup_2071_2100,  df_tempSup_2071_2100, df_evapot_2071_2100, df_ub, option1_precip_sup, option3_temp_sup, option5_evapot,'Ensamble_todos_2071_2100cedex')
                        with open('Ensamble_todos_2071_2100cedex.txt', 'r') as f:
                            arch_cedex6 = f.read()
                        f.close()


                        file_paths =['Ensamble_todos_2011_2040cedex.txt', 'Ensamble_todos_2041_2070cedex.txt', 'Ensamble_todos_2071_2100cedex.txt']

                        download_zip_file(file_paths)
                        with open("download.zip", "rb") as f:
                            bytes = f.read()
                            st.download_button(label="Descargar Archivos", data=bytes, file_name="Ensamble_todoscedex.zip", mime="application/zip")



































