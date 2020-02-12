# -*- coding: utf-8 -*-
"""
Jeff Yen
02/11/2020
Import multiple vehicle detector stations (VDS) tables to points
"""
# Initialize start time
import time
start = time.time()

# Set up workspace
import os
txt_in = os.path.dirname(os.getcwd()) + "\\Data"
os.chdir(txt_in)

# Import arcgis system modules
import arcpy

# Create a file geodatabase
print("Create a file geodatabase...")
path = txt_in
if arcpy.Exists(path) == False:
    arcpy.CreateFileGDB_management(path, "data")
else:
    arcpy.Delete_management(path+"\\data.gdb")
    arcpy.CreateFileGDB_management(path, "data")

# Import txt to geodatabase
import glob
import pandas as pd
files = glob.glob("*.txt")
outLocation = path + "\\data.gdb"
print("Importing tables to gdb: " + outLocation)
arcpy.TableToGeodatabase_conversion(files, outLocation)

# Set environment settings
arcpy.env.workspace = path+"\\data.gdb"
# Disable M and Z values to avoid PointZ/M output
arcpy.env.outputMFlag = "Disabled"
arcpy.env.outputZFlag = "Disabled"

# Set the local variables
x = "Longitude"
y = "Latitude"
z =""
SpatialRef = arcpy.SpatialReference(4326) #lat/long for GCS WGS84

# Make xy table to point
tbList = arcpy.ListTables()
for t in tbList:
    csv_in = t
    fc_out = t+"_poi"
    print("Make '{}' to point".format(t))
    arcpy.management.XYTableToPoint(csv_in, fc_out, x, y, z, SpatialRef)
    
    # Project to "NAD_1983_StatePlane_California_VI_FIPS_0406_Feet" (WKID = 2230)
    print("Project '{}' to 'NAD_1983_StatePlane_California_VI_FIPS_0406_Feet'".format(fc_out))
    arcpy.Project_management(fc_out, t+"_poi_sp6", arcpy.SpatialReference(2230))

# Output the execution time
from datetime import timedelta
end = (time.time() - start)
t = str(timedelta(seconds=end))
print ("Execute time: {}".format(t))
