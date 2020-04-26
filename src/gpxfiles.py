import os
import re
import pandas as pd

class GPXFile():
    '''Basic object to wrap a given GPX file.'''

    def __init__( self , filename ):
        
        self.filename = filename
        self.raw = self.load(self.filename)
        self.name = self.getTag(self.raw,"name")
        self.createTime = self.getTag(self.getTag(self.raw,"metadata"),"time")
        
        self.points = self.getTrackPoints(self.raw)
        self.pointsAsXML = pd.DataFrame(self.points.apply(lambda x : self.formatTrackPoint(x) , axis = 1 ))
        
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
    def __init__( self , filePaths ):
                
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
        sns.scatterplot(x="longitude",y="latitude",data = self.map)    
    

    def combine( self ):
        '''combine all tracks into one.'''

        # this needs some work.

        skeleton = self.data[0].raw
        head = skeleton.split("<trkseg>")[0]
        
        # include something to update the GPX creator tag AND the Name
        # clean up the GPX file
        
        tail = skeleton.split("</trkseg>")[1]
        body = "\n".join(self.pointsASXML[0].tolist())
        
        return(head + "\n<trkseg>\n" + body + "</trkseg>\n" +  tail)
    
    def export( self , outfilePath ):
        '''export combined track to XML / GPX file.'''
        with open( outfilePath , "w" ) as outfile:
            outfile.write(self.combine())
            
        
        
    
