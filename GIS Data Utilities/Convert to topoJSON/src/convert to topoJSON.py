# -*- coding: utf-8 -*-
"""
Convert Geospatial Data to TopoJSON

@author: Jeff Yen
"""
import os
import topojson as tp #topojson: https://mattijn.github.io/topojson/
import geopandas as gpd

# Set up workspace to the script directory
os.chdir(os.path.dirname(os.path.abspath('__file__')))

def tp_json_conversion(input_file_path, outname):
    #load input data as GeoDF
    input_data = gpd.read_file(input_file_path)
    
    #if input projection is not WGS84
    #then do re-projection
    if input_data.crs != "EPSG:4326":
        input_data = input_data.to_crs("EPSG:4326")
    
    #export geography to topojson
    resultTP = tp.Topology(input_data, prequantize=False).to_json()
    Output_object = open(r"..\output\{}.json".format(outname),"w")
    Output_object.write(resultTP)

    #export attribute table as csv (exclude geometry)
    input_data.iloc[:,:-1].to_csv(r'..\output\{}.csv'.format(outname), index = False)
    
    return resultTP


# Run data conversion
outname = "SD_City" #TODO: specify outfile name
input_file_path = r"..\data\Jurisdictions.shp" #TODO: specify geospatial file path
tp_json_conversion(input_file_path, outname)