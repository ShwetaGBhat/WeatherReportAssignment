#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 21 17:35:08 2021

@author: shwetabhat
"""
# =============================================================================
#Load libraries.
# =============================================================================
    
import argparse, os

import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt

# =============================================================================
# Helper Methods.
# =============================================================================
# =============================================================================
# The method used to parse the date-time. 
# =============================================================================

def parser(x):
	return datetime.strptime(x,'%Y%m%d%H%M')

# =============================================================================
# The method is used to plot the hottest and coldest days.
# =============================================================================

def plotSeries(days,imgName,timeOfTheYear="hottest"):  
    ax = days.plot(grid=True)
    ax.set_xlabel('Hour of a day.')
    ax.set_ylabel("Temperature")
    ax.set_title("For {} days of the year. ".format(timeOfTheYear), fontdict=None, loc='center')
    plt.savefig(imgName)
    plt.show()



# =============================================================================
#Read the file.
# =============================================================================
def readingFilePreprocessing(inputFile):
    data=pd.read_csv(inputFile,header=0)
    # =============================================================================
    # =============================================================================
    #Preprocessing the timestamp extracting the timecomposnents.
    # =============================================================================
    data["timeStamp"]=data["Zeitstempel"].apply(str).apply(parser)
    data['year']=data["timeStamp"].apply(lambda x: x.year)#data["timeStamp"].dt.year
    data['month']=data["timeStamp"].apply(lambda x: x.month)
    data['day']=data["timeStamp"].apply(lambda x: x.day)
    # =============================================================================
    data.index=data["timeStamp"]
    return data


def getHottestColdestDaysStatistics(data):
    # Grouping 
    # =============================================================================
    # 	•	Find the hottest and coldest temperature values for every year and their time of occurrence.
    # 	•	Store this information in a human-readable file (csv or other text file or graphic).
    # =============================================================================
    yearWiseGroupped=[data[data['year'] == y] for y in data['year'].unique()]
    i=0
    #Dataframe used to store the hot and cold days statistics. 
    tempStats=pd.DataFrame(columns=["Year","Month","Day","Hour","Minute","Second","Max_Temp","Min_Temp"])
    hotDays=pd.DataFrame()#dataframe contains hottest days temperature for 15 minutes interpolated.
    coldDays=pd.DataFrame()#dataframe contains coldest days temperature for 15 minutes interpolated.
      
    for y in  yearWiseGroupped:
        if yearWiseGroupped[i].index.year[0]!=2019 and yearWiseGroupped[i].index.year[0]!=2020 :
            #can reach as best quality check level. when Qualitaet_Niveau value is greater than or equal to 5.
            #for years 2019 and 2020 we can't interpolate as most of the data points 
            # for year 2019 value Qualitaet_Niveau:5,6,7 count of instances are 23
            # for year 2020 with Qualitaet_Niveau : 5,6,7=count of instances are nil and 
            #               with Qualitaet_Niveau : count of instances are 1345
        
            y1=y.query('Qualitaet_Niveau >= 5')
            yearWiseInterpolated=y1["Wert"].resample("15T").interpolate(method='linear')
        else:
            y1=y
            yearWiseInterpolated=y["Wert"].resample("15T").interpolate(method='linear')
        tempMaxDateTime=yearWiseInterpolated.idxmax()
        tempMinDateTime=yearWiseInterpolated.idxmin()
        tempMax=yearWiseInterpolated.max()
        tempMin=yearWiseInterpolated.min()
        #Converting the time steps of the temperature data to 15-minutes-intervals, using interpolation.
        cnt=0
        for key, sub_df in y1.groupby(['year', 'month',"day"]):
                        interploated=sub_df["Wert"].resample("15T").interpolate(method='linear')
                        if interploated.max()== tempMax:
                            cnt+=1
                            lable="Year:{}Month:{}Day:{}".format(interploated.index.year[0],+interploated.index.month[0],interploated.index.day[0])
                            hotDays=pd.concat([hotDays.reset_index(drop=True),pd.Series(data=list(interploated), index=interploated.index.time).rename(lable).reset_index(drop=True)], axis=1). reset_index(drop=True) 
                            hotDays.index=interploated.index.time
                        if interploated.min() == tempMin:
                            cnt+=1
                            lable="Year:{}Month:{}Day:{}".format(interploated.index.year[0],+interploated.index.month[0],interploated.index.day[0])
                            coldDays=pd.concat([coldDays.reset_index(drop=True),pd.Series(data=list(interploated), index=interploated.index.time).rename(lable).reset_index(drop=True)], axis=1). reset_index(drop=True) 
                            coldDays.index=interploated.index.time
    
        i+=1
        tempStats=tempStats.append({'Year':tempMaxDateTime.year,"Month":tempMaxDateTime.month,"Day":tempMaxDateTime.day,"Hour":tempMaxDateTime.hour,"Minute":tempMaxDateTime.minute,"Second":tempMaxDateTime.second,"Max_Temp":yearWiseInterpolated.max(),"Min_Temp":"-"}, ignore_index=True)
        tempStats=tempStats.append({'Year':tempMinDateTime.year,"Month":tempMinDateTime.month,"Day":tempMinDateTime.day,"Hour":tempMinDateTime.hour,"Minute":tempMinDateTime.minute,"Second":tempMinDateTime.second,"Max_Temp":"-","Min_Temp":yearWiseInterpolated.min()}, ignore_index=True)
        
    return tempStats,hotDays,coldDays




def dir_path(string):
    print("--Called dir_path")
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def file_path(dirPath,filePath):
    print("--Called file_path(path)")
    if os.path.exists(dirPath+os.sep+filePath):
       print("File exists.")
       return dirPath+os.sep+filePath
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{dirPath+os.sep+filePath} is not a valid path")

def parse_arguments():    
    parser = argparse.ArgumentParser()
    print("--Called parse_arguments()")
    parser.add_argument('--path', type=dir_path,help='Add the Directory path', metavar="dirPath",required=True)
    parser.add_argument('--input', help='the input file', required=True)
    parser.add_argument('--dest', help='the destination', required=True)

    return parser.parse_args()



def main():

    print("--Called Main()")
    parsed_args = parse_arguments()
    inputFile=file_path(parsed_args.path,parsed_args.input)
    destFile=parsed_args.dest
    data=readingFilePreprocessing(inputFile)
    tempStats,hotDays,coldDays=getHottestColdestDaysStatistics(data)
    # =============================================================================
    # 	•	Store the temperature statistics  in a human-readable file (csv or other text file or graphic).
    # =============================================================================
    #os.mkdir(, 0755 );
    print(parsed_args.path+os.sep+"output")
    os.mkdir(parsed_args.path+os.sep+"output", mode=0o755)
    tempStats.to_csv(parsed_args.path+os.sep+"output"+os.sep+destFile,index=False)
    # =============================================================================
    # =============================================================================
    # 	•	Plot the hottest and cold days.
    # =============================================================================
    plotSeries(hotDays,parsed_args.path+os.sep+"output"+os.sep+"HotDays.png","hottest",)
    plotSeries(coldDays,parsed_args.path+os.sep+"output"+os.sep+"ColdDays.png","coldest",)

if __name__ == "__main__":
    main()


# =============================================================================
# References:
# =============================================================================
#     1.https://towardsdatascience.com/pandas-resample-tricks-you-should-know-for-manipulating-time-series-data-7e9643a7e7f3
#     2.https://machinelearningmastery.com/resample-interpolate-time-series-data-python/
#     3.https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html
#     4.https://stackoverflow.com/questions/46011940/how-to-plot-two-pandas-time-series-on-same-plot-with-legends-and-secondary-y-axi
# =============================================================================
