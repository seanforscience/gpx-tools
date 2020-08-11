import os
import re
import math
import pandas as pd
import datetime as dt



def haversine( point1 , point2 ):
    '''haversine distance formula.'''
    lat1, lon1 = point1
    lat2, lon2 = point2
    radius = 6371

    deltaLat = math.radians(lat2-lat1)
    deltaLon = math.radians(lon2-lon1)
    
    alpha = math.sin(deltaLat/2) * math.sin(deltaLat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(deltaLon/2) * math.sin(deltaLon/2)
    gamma = 2 * math.atan2(math.sqrt(alpha), math.sqrt(1-alpha))

    distance = radius * gamma

    return(distance)



class GPXFile():
    '''Basic object to wrap a given GPX file.'''

    def __init__( self , filename ):
        
        self.filename = filename
        self.raw = self.load(self.filename)
        self.name = self.getTag(self.raw,"name")
        self.createTime = self.getTag(self.getTag(self.raw,"metadata"),"time")
        
        self.points = self.getTrackData(self.raw)
        self.pointsAsXML = pd.DataFrame(self.getTrackPoints(self.raw).apply(lambda x : self.formatTrackPoint(x) , axis = 1 ))
        
    def getTag( self , field , tagname):
        '''basic XML tag extractor'''
        return(field.split("<"+tagname+">")[1].split("</"+tagname+">")[0])
        
    def getTrackPoints( self , track ):
        '''extract all trackpoints as dataframe of literal strings. '''
        trackSegment = track.split("<trkseg>")[1].split("/<trkseg>")[0]
        
        rawPoints = pd.Series([x.split("</trkpt>")[0] for x in trackSegment.split("<trkpt ") if "lat" in x])
        output = pd.DataFrame()
    
        getAttribute = lambda field , name : re.findall("[-0-9.]+",re.findall(name+"=\"[-0-9.]+\"",field)[0])[0]

        output["latitude"] = rawPoints.apply( lambda x : getAttribute(x,"lat"))
        output["longitude"] = rawPoints.apply( lambda x : getAttribute(x,"lon"))
        output["elevation"] = rawPoints.apply(lambda x : self.getTag(x,"ele"))
        output["time"] = rawPoints.apply(lambda x : self.getTag(x,"time"))
        return(output)        

    def getTrackData( self , track ):
        data = self.getTrackPoints( track ).copy()
        for field in ["latitude","longitude","elevation"]:
            data[field] = data[field].apply(float)
        data["time"] = data["time"].apply(lambda t : dt.datetime.strptime(t,"%Y-%m-%dT%H:%M:%SZ")) 
        data["source"] = self.filename
        # note. Z here stands for zulu, which means UTC +0

        data = self.enrichData( data )

        return(data)

    def enrichData( self , data ):

        distances = data[["latitude","longitude"]].copy()
        distances = distances.join(distances.shift(-1),lsuffix="_1",rsuffix="_2").dropna()
        data["distance"] = distances.apply(lambda x : haversine([x["latitude_1"],x["longitude_1"]],[x["latitude_2"],x["longitude_2"]]) , axis = 1)

        return(data)

        
    def load( self , filePath ):
        '''load the raw GPX file as text.'''
        with open( filePath , "r" ) as infile:
            gpx = infile.read()
        return(gpx)        
        
        
    def formatTrackPoint( self , dataRow ):
        '''format a row of track point dataframe as XML tag trkpt'''
        lat = dataRow.get("latitude")
        lon = dataRow.get("longitude")
        ele = dataRow.get("elevation")
        time = dataRow.get("time")
        dressTag = lambda tag , name : "<"+name+">" + tag + "</"+name+">\n"
        junk = dressTag(ele,"ele") + dressTag(time,"time")
        output = "<trkpt lat=\"" + lat + "\" lon=\"" + lon + "\">\n" + junk + "</trkpt>\n"
        
        return(output)  
    
    
class GPXFiles():
    def __init__( self , filePaths , outputName = "combined" ):
                
        self.outputName = outputName
        self.data = self.loadData( filePaths)
        self.points = pd.concat(list(self.data.apply(lambda x : x.points)))
        self.pointsASXML = pd.concat(list(self.data.apply(lambda x : x.pointsAsXML)))
        
        self.map = self.points[["longitude","latitude","elevation"]].applymap(float)
        
    def loadData( self , paths ):
        '''load the given trackpoints from list of complete filepaths.'''

        ## load each file as a GPXFile
        data = pd.Series([GPXFile(file) for file in paths])
        
        ## sort by time the GPX file was recorded
        data = data.loc[data.apply(lambda x : x.createTime).sort_values().index]        
        
        ## reindex
        data.index = range(len(data))        
        
        return(data)
    
    def plotPoints( self ):
        '''if you have seaborn installed, here's a quick way to visualize your tracks as a map.'''

        import seaborn as sns        
        import matplotlib.pyplot as plt # needed to call the visual
        sns.scatterplot(x="longitude",y="latitude",data = self.map)
        plt.show()
    

    def combine( self ):
        '''combine all tracks into one.'''

        skeleton = self.data[0].raw
        head = skeleton.split("<trkseg>")[0]
        newCreatorString = "SeanForScience GPX toolkit"
        
        # include something to update the GPX creator tag AND the Name
        try:
            creator = re.findall("gpx creator=\"(.*?)\"",self.data[0].raw)[0]
            head = head.replace(creator,newCreatorString)
        except:
            print("regex error in gpx creator name.")


        # rename the file
        try:
            oldName = re.findall("<name>(.*?)</name>",self.data[0].raw)[0]
        except:
            oldName = self.outputName
            print("regex error in GPX file name.")

        head = head.replace(oldName,self.outputName)

        tail = skeleton.split("</trkseg>")[1]
        body = "\n".join(self.pointsASXML[0].tolist())
        
        return(head + "\n<trkseg>\n" + body + "</trkseg>\n" +  tail)
    
    def export( self , outfilePath ):
        '''export combined track to XML / GPX file.'''
        with open( outfilePath , "w" ) as outfile:
            outfile.write(self.combine())
            
        
        
    
