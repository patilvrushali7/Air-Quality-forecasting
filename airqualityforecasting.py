# -*- coding: utf-8 -*-
"""AirQualityForecasting.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Vy7p2lyzpdIa1THADXCCVK2j2m1yO23e
"""

# Commented out IPython magic to ensure Python compatibility.
# importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from numpy import sqrt,log
from scipy.stats import boxcox
import statsmodels.formula.api as smf 
from statsmodels.tsa.api import ExponentialSmoothing, SimpleExpSmoothing, Holt
from sklearn.metrics import mean_squared_error
import statsmodels.formula.api as smf 
import warnings
# %matplotlib inline

#loading dataset
co2 = pd.read_excel("\\Users\\piyus\\Documents\\ExcelR project\\P90\\CO2 dataset.xlsx")
co2.head()

#size of dataset
co2.shape

#data distribution
co2.CO2.describe()

#checking for NAN values
co2.isna().sum()

#data types
co2.dtypes

#checking for time intervals
x=co2.Year.diff()
for i in  x:
    if i == 1:
        pass
    else:
        print(i)

data=co2.copy()

"""#### converting the float to datetime format"""

Year = pd.date_range(start="1/1/1800",end="1/1/2015",freq='A')
Year

data=data.drop(['Year'],axis=1)
data['Year'] =Year
#data['Year'] = pd.to_datetime(data['Year'], format='%Y')
#
#data=data.drop(['Year'],axis=1)
data.set_index(data.Year,inplace=True)
#data=data.drop(['Year'],axis=1)
data=data.iloc[:,0:1]
data.head()

data.dtypes

"""### Analysing Data With Graphs"""

#line plot
data.plot(color='black')
plt.xlabel("Year")
plt.ylabel("Co2 ")
plt.grid()
plt.show()

"""  **from above lineplot shows that C02 emission over the period of time is increasing therefore data is showing exponential trend but no seasonality is present in data."""

from statsmodels.tsa.seasonal import seasonal_decompose
decompose = seasonal_decompose(data.CO2)
decompose.plot()
plt.grid()
plt.show()

"""**Seasonal demoposition shows that 
 1. avarage is not constant for the co2 emission over the period of time
 2. there is a tred followed by data which is of exponential type 
 3. seasonality is not present in the data
 4. there are no residuals
"""

data.plot(kind='kde')

#lag plot
from pandas.plotting import lag_plot
lag_plot(data,)
plt.grid()
plt.show()

"""**lag plots shows that there is positive liner relation between variable and its own lag variable """

from pandas.plotting import autocorrelation_plot
autocorrelation_plot(data)
plt.show()

import statsmodels.graphics.tsaplots as tsa_plots
tsa_plots.plot_acf(data.CO2)
plt.show()

"""**from the above graph we can examine that nearest time lag has good autocorrelation but as we reach time      period which are far away the autocorrelation is decressing"""



"""Modifing the data 
* including columns : "t"-time,"t_square"-time square,"log_co2"-log of Co2
"""

data_1=data.copy()
data_1["t"] = np.arange(1,216)
data_1["t_squared"] = data_1["t"]*data_1["t"]
data_1["log_CO2"] = np.log(data["CO2"])
data_2=data_1.drop(['CO2'],axis=1)
data_3=data_2.drop(['log_CO2'],axis=1)
data_1.head()

"""### splitting modified data into training and testing"""

train_1=data_1.head(172)
test_1=data_1.tail(43)

test_1.shape



"""#### square_root transformation"""

## square_root transformation

sqrt_ = pd.DataFrame()
sqrt_['CO2'] = sqrt(data['CO2'])

sqrt_=pd.concat([sqrt_,data_3],axis=1)
sqrt_["log_CO2"]=np.log(sqrt_["CO2"])
train_sqrt_=sqrt_.head(172)
test_sqrt_=sqrt_.tail(43)

def inverse_sqrt(datat__):
    inv_sqrt = datat__*datat__
    return inv_sqrt

"""#### log transformation"""

Log_ = pd.DataFrame()
Log_['CO2'] = log(data['CO2'])
Log_.head()
Log_=pd.concat([Log_,data_3],axis=1)
Log_["log_CO2"]=np.log(Log_["CO2"])
train_Log_=Log_.head(172)
test_Log_=Log_.tail(43)

def inverse_log(log_data):
    in_log=np.exp(log_data)
    print(in_log)

"""#### boxcox Transformation"""

from scipy.stats import boxcox
from math import exp
# box-cox transform
result, lmbda = boxcox(data['CO2'])
boxcox_ = pd.DataFrame(result, columns=['CO2'])

boxcox_["t"]=np.arange(1,216)

boxcox_["t_squared"]=boxcox_["t"]*boxcox_["t"]
boxcox_["log_CO2"]=np.log(boxcox_['CO2'] )
boxcox_['log_CO2']=boxcox_['log_CO2'].fillna(0)

train_boxcox_=boxcox_.head(172)
test_boxcox_=boxcox_.tail(43)
#invert difference
def invert_boxcox(value, lam):
    if lam == 0:
        return exp(value)
    return exp(log(lam * value + 1) / lam)

"""#### resreciprocal transformation"""

rec=np.reciprocal(data.CO2)
recipro=pd.DataFrame(rec,columns=['CO2'])
recipro=pd.concat([recipro,data_3],axis=1)
recipro['log_CO2']=np.log(recipro['CO2'])
train_recipro=recipro.head(172)
test_recipro=recipro.tail(43)

#spliting the original data into training and testing set
train=data.head(172)
test=data.tail(43)



"""## Function to build model on "Naives Aproch ", " Simple Average "," Moving Average "
"""

from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score


def errors1 (train,test):
    moddel= {
        'Naives Aproch' : {
            'model' : np.asarray(train.CO2)[len(np.asarray(train.CO2))-1]
        
    },
        'Simple Average' : {
            
            'model' : train['CO2'].mean()
        },
        'Moving Average' :{
            'model' : train['CO2'].rolling(2).mean().iloc[-1]
        }
        
}
    scores = []
    for moddel_name, config in moddel.items():
        gs =  config['model']
        scores.append({
            'model': moddel_name,
            'result':  np.mean(np.abs((gs-test.CO2)/test.CO2)*100)

        })
   
    return pd.DataFrame(scores,columns=['model','result'])

"""### putting the result into singal dataframe.

"""

result_driven = pd.DataFrame()
a_=errors1(train,test)
a=a_.rename(columns={'result':'original_error'},inplace=True)
b_=errors1(train_sqrt_,test_sqrt_)
b=b_.rename(columns={'result':'sqrt_error'},inplace=True)
c_=errors1(train_Log_,test_Log_)
c=c_.rename(columns={'result':'log_error'},inplace=True)
d_=errors1(train_boxcox_,test_boxcox_)
d=d_.rename(columns={'result':'BoxCox_error'},inplace=True)
#e_=errors1(train_Scaler_,test_Scaler_)
#e=e_.rename(columns={'result':'MinMax_error'},inplace=True)
f_=errors1(train_recipro,test_recipro)
f=f_.rename(columns={'result':'recipro_error'},inplace=True)
result_driven = pd.concat([a_,b_.drop(['model'],axis=1),c_.drop(['model'],axis=1),d_.drop(['model'],axis=1),f_.drop(['model'],axis=1)],axis=1)
result_driven



"""## Function to build model on "Simple Exponential ", " Holts "."""

def errors2 (train,test):
    mooodel={
        "Simple Exponential" :{
            'model': SimpleExpSmoothing(np.asarray(train['CO2'])).fit(smoothing_level=0.9)
        },
        "Holts" :{
            'model':Holt(np.asarray(train['CO2'])).fit(smoothing_level = 0.1,smoothing_slope = 0.1)
        }
    }
    
    scores = []
    for moddel_name, config in mooodel.items():
        gs =  config['model']
        pred = gs.forecast(len(test))
        scores.append({
            'model': moddel_name,
            'result':  np.mean(np.abs((pred-test.CO2)/test.CO2)*100)

        })
   
    return pd.DataFrame(scores,columns=['model','result'])

#putting result into single data frame
warnings.filterwarnings("ignore")
result_exp = pd.DataFrame()
x_=errors2(train,test)
x=x_.rename(columns={'result':'original_error'},inplace=True)
y_=errors2(train_sqrt_,test_sqrt_)
y=y_.rename(columns={'result':'sqrt_error'},inplace=True)
z_=errors2(train_Log_,test_Log_)
z=z_.rename(columns={'result':'log_error'},inplace=True)
v_=errors2(train_boxcox_,test_boxcox_)
v=v_.rename(columns={'result':'BoxCox_error'},inplace=True)
#u_=errors2(train_Scaler_,test_Scaler_)
#u=u_.rename(columns={'result':'MinMax_error'},inplace=True)
nx_=errors2(train_recipro,test_recipro)
nx=nx_.rename(columns={'result':'recipro_error'},inplace=True)
result_exp = pd.concat([x_,y_.drop(['model'],axis=1),z_.drop(['model'],axis=1),v_.drop(['model'],axis=1),nx_.drop(['model'],axis=1)],axis=1)
result_exp



"""## Function to build model on "Simple Liner model ", " Exponential Linear model "."""

def errors3 (train,test):
    mooodel={
        "Simple Liner model" :{
            'model': smf.ols('CO2~t',data=train).fit()
        },
        "Exponential Linear model" :{
            'model': smf.ols('log_CO2~t',data=train).fit()
        }
    }
    scores = []
    for moddel_name, config in mooodel.items():
        gs =  config['model']
        pred = pd.Series(gs.predict(test["t"]))
        scores.append({
            'model': moddel_name,
            'result':  np.mean(np.abs((pred-test.CO2)/test.CO2)*100)
        })
    return pd.DataFrame(scores,columns=['model','result'])

##putting data into single dataframe
result_linear = pd.DataFrame()
k_=errors3(train_1,test_1)
k=k_.rename(columns={'result':'original_error'},inplace=True)
l_=errors3(train_sqrt_,test_sqrt_)
l=l_.rename(columns={'result':'sqrt_error'},inplace=True)
m_=errors3(train_Log_,test_Log_)
m=m_.rename(columns={'result':'log_error'},inplace=True)
t_=errors3(train_boxcox_,test_boxcox_)
t=t_.rename(columns={'result':'BoxCox_error'},inplace=True)
nc_=errors3(train_recipro,test_recipro)
nc=nc_.rename(columns={'result':'recipro_error'},inplace=True)
result_linear = pd.concat([k_,l_.drop(['model'],axis=1),m_.drop(['model'],axis=1),t_.drop(['model'],axis=1),nc_.drop(['model'],axis=1)],axis=1)
result_linear



"""## Function to build model on "holts winter method"
"""

def holtserrors (train,test):
    mooodel={
        "Holts Winter" :{
            'model': ExponentialSmoothing(train.CO2).fit()
        }
    }
    
    scores = []
    for moddel_name, config in mooodel.items():
        gs =  config['model']
        pred = gs.forecast(len(test))
        scores.append({
            'model': moddel_name,
            'result':  np.mean(np.abs((pred-test.CO2)/test.CO2)*100)

        })
   
    return pd.DataFrame(scores,columns=['model','result'])

warnings.filterwarnings("ignore")
holts_k_=holtserrors(train_1,test_1)
holts_k=holts_k_.rename(columns={'result':'original_error'},inplace=True)
holts_l_=holtserrors(train_sqrt_,test_sqrt_)
holts_l=holts_l_.rename(columns={'result':'sqrt_error'},inplace=True)
holts_m_=holtserrors(train_Log_,test_Log_)
holts_m=holts_m_.rename(columns={'result':'log_error'},inplace=True)
holts_t_=holtserrors(train_boxcox_,test_boxcox_)
holts_t=holts_t_.rename(columns={'result':'BoxCox_error'},inplace=True)
holts_nc_=holtserrors(train_recipro,test_recipro)
holts_nc=holts_nc_.rename(columns={'result':'recipro_error'},inplace=True)
HoltsWinter_ = pd.concat([holts_k_,holts_l_.drop(['model'],axis=1),holts_m_.drop(['model'],axis=1),holts_t_.drop(['model'],axis=1),holts_nc_.drop(['model'],axis=1)],axis=1)
HoltsWinter_



"""### All the Errors for different Transformation technique"""

final_result_all = pd.concat([result_driven,result_exp,result_linear,HoltsWinter_],axis=0)
final_result_all

"""                             Navie Aproch , Simple Exponential and Holts Winter metod has given least error with LogTransformation .
As Navie Aproch work well when data set contain less variance but that's not a case with our data ,our data have high variance therefore we didnot gone with it and decided to go with Holts Winter Method.
"""



"""# ARIMA

### Function for adfuller test
"""

from statsmodels.tsa.stattools import adfuller
def test_adfuller(data):
     adf_test = adfuller(data, autolag = 'AIC')
     print("1. ADF : ",adf_test[0])
     print("2. P-Value : ", adf_test[1])
     print("3.  Lags : ", adf_test[2])
     print("4. Num Of Observations :",      adf_test[3])
     print("5. Critical Values :")
     for key, val in adf_test[4].items():
         print("\t",key, ": ", val)

test_adfuller(data['CO2'])

test_adfuller(sqrt_['CO2'])

test_adfuller(Log_['CO2'])

test_adfuller(boxcox_['CO2'])

test_adfuller(recipro['CO2'])

"""From adfuller test we came to know that reciprocal Transformation is givig least p_values so we will build arima model on Reciprocal Transformation"""

# auto arima to get best p,d,q

from pmdarima import auto_arima
show_fit = auto_arima(recipro['CO2'], trace=True,suppress_warnings=True)

from statsmodels.tsa.arima_model import ARIMA
model=ARIMA(train_recipro['CO2'],order=(0,1,0))
model=model.fit()
warnings.filterwarnings("ignore")

start=len(train_recipro.CO2)
end=len(train_recipro.CO2)+len(test_recipro.CO2)-1
pred2_=model.predict(start=start,end=end,typ='levels').rename('ARIMA Predictions')
np.mean(np.abs((pred2_-test_recipro.CO2)/test_recipro.CO2)*100)

"""#### ARIMA can't outperform  Holts Winter Method therefore our final model will be build on  Holts Winter Method"""



"""## Final model with Holts Winter Method"""

HoltsWinter_final = ExponentialSmoothing(Log_.CO2,seasonal="add",trend="add",seasonal_periods=12).fit()
HoltsWinter_pred = HoltsWinter_final.predict(start = Log_.CO2.index[0],end = Log_.CO2.index[-1])

np.mean(np.abs((HoltsWinter_pred-Log_.CO2)/Log_.CO2)*100)

data['Forecast']=np.exp(HoltsWinter_pred)



plt.plot(data['CO2'], label='Test')
plt.plot(data['Forecast'], label='SES')
plt.legend(loc='best')
plt.grid()
plt.show()

"""### Predicting CO2 values for next 10 years"""



np.exp(HoltsWinter_final.forecast(10))



import pickle
filename = 'C:/Users/piyus/Downloads/air_quality_forecast.sav'
pickle.dump(HoltsWinter_final, open(filename, 'wb'))

# .pickle file
with open('C:/Users/piyus/Downloads/air_quality_forecasts.pickle','wb') as f:
    pickle.dump(HoltsWinter_final,f)

final_df = data.CO2
#For Deployment
final_df.to_pickle("C:/Users/piyus/Downloads/air_final_df.pickle")
final_df.to_csv("C:/Users/piyus/Downloads/CO2_Cleaned_data.csv")