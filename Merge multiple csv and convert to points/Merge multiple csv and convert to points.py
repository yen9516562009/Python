# -*- coding: utf-8 -*-
"""
Jeff Yen
02/04/2020
Merge multiple csv and convert to points
"""
# Initialize start time
import time
start = time.time()

# Set up workspace
import os
os.chdir(r"C:\Users\Y\OneDrive\WorkSample\Python")
os.getcwd()

# Merge multiple csv files in subdirectories
import glob
import pandas as pd
files = glob.glob("*/*/*.csv")
df = pd.concat([pd.read_csv(f) for f in files])
df.to_csv("merged.csv")
print("Merging csv...")

# Import arcgis system modules
import arcpy

# Create a file geodatabase
dir_in = os.getcwd() #retrieve current .py directory
path = dir_in + "\\data.gdb"
if arcpy.Exists(path) == False:
    arcpy.CreateFileGDB_management(dir_in, "data")
else:
    arcpy.Delete_management(path)
    arcpy.CreateFileGDB_management(dir_in, "data")

# Set environment settings
arcpy.env.workspace = path
# Disable M and Z values to avoid PointZ/M output
arcpy.env.outputMFlag = "Disabled"
arcpy.env.outputZFlag = "Disabled"

# Set the local variables
csv_in = dir_in+"\\merged.csv"
fc_out = "all_poi"
x = "Longitude"
y = "Latitude"
z =""
SpatialRef = arcpy.SpatialReference(4326) #lat/long for GCS_WGS84

# Make xy table to point
arcpy.management.XYTableToPoint(csv_in, fc_out, x, y, z, SpatialRef)

# Print the total rows
print("Total count: ",arcpy.GetCount_management(fc_out)) #check total # of rows = 51440

# Project to "NAD_1983_StatePlane_California_VI_FIPS_0406_Feet" (WKID = 2230)
arcpy.Project_management(fc_out, "all_poi_sp6", arcpy.SpatialReference(2230))

# Output the execution time
from datetime import timedelta
end = (time.time() - start)
t = str(timedelta(seconds=end))
print ("Execute time: {}".format(t))
