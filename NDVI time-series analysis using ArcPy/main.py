"""
Title: geog596_final_project_Jeff
Name: Jeff Yen
RedID: 821274604
Date: 04/26/2018
"""
import arcpy
from arcpy.sa import*
import csv

##Part 1
arcpy.AddMessage("\n##########Part1: Reading Image Info.##########")
img_res = arcpy.GetParameterAsText(0) #Get image resolution from user  

#Read required attribures: image path, time stamp, ndvi threshold
arcpy.AddMessage("\nReading image path, time stamp, and ndvi threshold...")
with open('C:/GEOG683_Program/Image_Info/image_info.csv', 'r') as f:
#with open('C:/Program/Image_Info/test.csv', 'r') as f:
  reader = csv.reader(f)
  attr_list = list(reader)
img_path = []
time_stamp = []
ndvi_thres = []
for i in range (1, len(attr_list)):
    if img_res == "A":
        #image (30m) file path
        img_path.append(attr_list[i][0])
    elif img_res == "B":
        #image (1m) file path
        img_path.append(attr_list[i][1])
    else:
        arcpy.AddMessage("Selected image spatial resolution is out of range : (")
        #####Add exit function to end this script
    #time stamp
    t = int(attr_list[i][2])
    time_stamp.append(t)
    #ndvi threshold
    n = float(attr_list[i][3])
    ndvi_thres.append(n)

#Calculate the number of input images
num_img = len(img_path)

def NDVI_Calculation(img_path, time_stamp):
    arcpy.AddMessage("\nCalculating {}NDVI...".format(time_stamp))
    # Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")
    
    #Set up workspace
    arcpy.env.workspace = r"C:/GEOG683_Program/Output/NDVI"
    result = ("{}NDVI.tif".format(time_stamp))
    
    #NDVI Calculation
    R = arcpy.Raster(img_path+'/Band_1')
    NIR = arcpy.Raster(img_path+'/Band_4')
    
    """
    Original NDVI value is from -1 to 1. Water/Impervious Surface (-1) ~ Mix(0) ~ Vegetation(1)
    Here I stretch NDVI value to 0 - 200 to avoid negative value. Water/Impervious Surface (0) ~ Mix(100) ~ Vegetation(200)
    """
    NDVI = arcpy.sa.Int((arcpy.sa.Float(NIR - R) / arcpy.sa.Float(NIR + R)) * 100) + 100
    
    #Output NDVI
    NDVI.save(result)
    
    return NDVI

def Vegetation_Classification(img_path, time_stamp, ndvi_threshold): #4/27 transfer this function to a moudle
    ##NDVI Calculation (2010NDVI, 2012NDVI, 2014NDVI, 2016NDVI)
    NDVI = NDVI_Calculation(img_path, time_stamp)

    #Set up workspace
    arcpy.env.workspace = r"C:/GEOG683_Program/Output/ndviVEG"
    result = ("{}ndviVEG.tif".format(time_stamp))
    
    #Vegetation Classification
    ndvi_threshold = int(ndvi_threshold)
    whereClause = ("VALUE < {}".format(ndvi_threshold)) #Set local variables (con)
    arcpy.AddMessage("Classifying {}Vegetation...".format(time_stamp))
    ndviVEG = arcpy.sa.SetNull(NDVI, NDVI, whereClause)
    #ndviVEG.save(result)
    
    ##Generate Binary Vegetation Classification Map
    arcpy.AddMessage("Generating {}Binary Vegetation Map...".format(time_stamp))
    
    # Define the RemapValue Object
    maxNDVI = arcpy.GetRasterProperties_management(NDVI, "MAXIMUM")
    arcpy.env.workspace = r"C:/GEOG683_Program/Output/VEG"
    result = ("{}VEG.tif".format(time_stamp))
    VEG_Range = RemapRange([[0, ndvi_threshold, 0], [ndvi_threshold, maxNDVI,1]])
    
    # Execute Reclassify
    VEG = Reclassify(NDVI, "VALUE", VEG_Range)
    VEG.save(result)
    
    return ndviVEG

def NDVI_Change_Detection(ndviList, num_img, time_stamp):   
    ##Vegetation Coverage Change (T1, T2, T3)
    arcpy.AddMessage("\nCalculating the Change of NDVI Value...")
    #Set up workspace
    arcpy.env.workspace = r"C:/GEOG683_Program/Output/CN"
    #Calculating the Change of NDVI Value
    CN = []
    for i in range(num_img-1):
        CN.append(ndviList[i+1]-ndviList[i]) #Vegetation Coverage Change = T1(2012-2010), T2(2014-2012), T3(2016-2014)
        result = ("T{}_CN.tif".format(i+1))
        CN[i].save(result)

    ##Vegetation Coverage Change Speed
    arcpy.AddMessage("\nCalculating the Speed of NDVI Value Change...")
    #Set up workspace
    arcpy.env.workspace = r"C:/GEOG683_Program/Output/SNC"
    #Calculating the Speed of NDVI Value Change
    SNC = []
    for i in range(num_img-2):
        SNC.append((CN[i+1]-CN[i])/(time_stamp[i+1]-time_stamp[i])) #Vegetation Coverage Change Speed = S1(T2-T1)/period(time2-time1), S2(T3-T2)/period(time3-time2)
        result = ("S{}_SNC.tif".format(i+1))
        SNC[i].save(result)  
    
    ##Vegetation Coverage Change Acceleration
    arcpy.AddMessage("\nCalculating the Acceleration of NDVI Value Change...")
    #Set up workspace
    arcpy.env.workspace = r"C:/GEOG683_Program/Output/ANC"
    #Calculating the Acceleration of NDVI Value Change
    ANC = []
    for i in range(num_img-3):
        ANC.append(SNC[i+1]-SNC[i]/(time_stamp[i+1]-time_stamp[i])) #Vegetation Coverage Change Speed = A1(S2-S1)/period(time2-time1)
        result = ("A{}_ANC.tif".format(i+1))
        ANC[i].save(result)
        
##Part 2
arcpy.AddMessage("\n##########Part2: Vegetation Classification##########")
#Append Vegetation Classification (2010VEG, 2012VEG, 2014VEG, 2016VEG) into a list
ndviList = []
for i in range(num_img):
    #Vegetation_Classification(img_path[i], time_stamp[i], ndvi_thres[i])
    ndviList.append(Vegetation_Classification(img_path[i], time_stamp[i], ndvi_thres[i]))

##Part 3
arcpy.AddMessage("\n##########Part3: Vegetation Change Detection##########")
NDVI_Change_Detection(ndviList, num_img, time_stamp)
