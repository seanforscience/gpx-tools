import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from gpxfiles import *


def haversine(originPair, destinationPair):
    '''Great Circle Distance in terms of GPS coordinates.'''
    lat1, lon1 = originPair
    lat2, lon2 = destinationPair
    earthRadius = 6371 

    deltaLat = pd.np.radians(lat2-lat1)

    deltaLon = pd.np.radians(lon2-lon1)
    
    alpha = pd.np.sin(deltaLat/2) * pd.np.sin(deltaLat/2) + pd.np.cos(pd.np.radians(lat1)) \
        * pd.np.cos(pd.np.radians(lat2)) * pd.np.sin(deltaLon/2) * pd.np.sin(deltaLon/2)
    beta = 2 * pd.np.arctan2(pd.np.sqrt(alpha), pd.np.sqrt(1-alpha))
    
    d = earthRadius * beta

    return(d)



class HeatMap():
    def __init__( self , path ):
        self.path = path
        self.files = [path + file for file in os.listdir(path)]
        self.rawData = GPXFiles(self.files).points

        self.data = self.build()
        
    def build( self ):
        
        data = self.rawData.copy()
        
        # TODO : use this filename based data to create or check a taxonomy for runs
        data["source"] = self.rawData.source.apply(lambda x : re.findall( "2020(.*)" , x)).apply(lambda x : "2020" + x[0])        
        
        # days
        data["daysAgo"] = data["time"].apply(lambda x : dt.datetime.today() - x ).apply(lambda x : x.total_seconds()).apply(lambda x : x / 3600 / 24 ).apply(int)        

        reference = list(data[["latitude","longitude"]].min())

        data["east"] = data["longitude"].apply(lambda x : haversine([reference[0],x],reference))
        data["north"] = data["latitude"].apply(lambda x : haversine([x,reference[1]],reference))
        
        return(data)

    def export( self ):
        '''save the plots to file'''

        figure = sns.scatterplot(x="longitude",y="latitude", data=self.data , hue="daysAgo" , edgecolor="none" , palette="Blues_r" , legend=None, sizes=(15, 15) )
        figure.set_aspect(1)
        figure.set_title("Trail Vlogging Heatmap: Lat Lon")
        toShow = figure.get_figure()
        figure.set_aspect(1)
        toShow.savefig("ll_output.png")

    def exportScaled( self ):
        '''save the flattened/scaled plots to file.'''

        figureScaled = sns.scatterplot(x="east",y="north", data=self.data , hue="daysAgo" , edgecolor="none" , palette="Blues_r" , legend=None, sizes=(15, 15) )
        figureScaled.set_aspect(1)
        figureScaled.set_title("Trail Vlogging Heatmap")
        toShowScaled = figureScaled.get_figure()
        figureScaled.set_aspect(1)
        toShowScaled.savefig("km_output.png")
