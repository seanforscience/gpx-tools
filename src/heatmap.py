import os
import pandas as pd
from gpxfiles import GPXFile

class HeatMap():
    def __init__( self , data = pd.DataFrame() ):
        self.data = data
        self.dress()
        
    def sources( self ):
        try:
            output = self.data.source.unique()
        except:
            output = []
        return(output)
        
    def intake( self , file ):
        
        sources = self.sources()
        if file not in sources:
            data = GPXFile(file).points        
            print( "processing " + file + "...")
            self.data = pd.concat([self.data,data])
            print("done.")
            
    def compilation( self , files ):
        for file in sorted(files):
            self.intake(file)
            
        self.dress()
        
    def export( self , path , dressed = False):
        
        output = self.data
        if dressed:
            output = self.dressed()
        
        self.data.to_csv( path , index = None)

    def dress( self ):
        
        metaData = lambda filename : dict(zip(["date","trailname","region"],filename.split("/")[-1].split(".")[0].split("_")))
        output = self.data.join(pd.DataFrame(self.data.source.apply(metaData).tolist()))
        output = output[[c for c in output.columns if c != "source"]]
        
        self.dressed = output

class HistoricalHeatMap(HeatMap):
    def __init__(self):
    
        self.dataPath = "/Volumes/TheMonster/GPS/Strava/"
        self.path = "/Volumes/TheMonster/GPS/HeatMap/heatmap.csv"
        print("loading...")
        
        try:
            data = pd.read_csv(self.path)
        except:
            data = pd.DataFrame()
            
        HeatMap.__init__( self , data )
        self.update()
        
    def update( self ):
        
        gpxFiles = [self.dataPath + x for x in os.listdir(self.dataPath) if x.startswith("2")]
        self.compilation(gpxFiles)
        self.export(self.path)
