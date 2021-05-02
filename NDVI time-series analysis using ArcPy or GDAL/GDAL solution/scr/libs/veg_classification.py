import gdal
import numpy as np
import libs.outputraster as otr

def NDVI_Calculation(img, time_stamp, ndvi_threshold):
    #Free memory
    NDVI = None
    
    #Read input image
    dataset = gdal.Open(img, gdal.GA_ReadOnly) 
    
    #Get raster properties
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    projection = dataset.GetProjection()
    geotransform = dataset.GetGeoTransform()
    metadata = dataset.GetMetadata()
    
    #Get R and NIR bands from each input image
    band1 = dataset.GetRasterBand(1)  #R
    band4 = dataset.GetRasterBand(4)  #NIR
    
    #Reading the raster values into a 2D numeric array
    R = band1.ReadAsArray(0, 0, cols, rows).astype(float) #to keep folat and avoid division error of 0 if there is a 0
    NIR = band4.ReadAsArray(0, 0, cols, rows).astype(float)
        
    #NDVI Calculation
    print ("Calculating {}NDVI...".format(time_stamp))
    
    #Original NDVI value is from -1 to 1. Water/Impervious Surface (-1) ~ Mix(0) ~ Vegetation(1)
    #Here I stretch NDVI value to 0 - 200 to avoid negative value. Water/Impervious Surface (0) ~ Mix(100) ~ Vegetation(200)
    NDVI = (((NIR-R)/(NIR+R+0.000000001))*100).astype(int)+100 #+0.0000000000000001 is for macOS environment
    
    #Set background value to 0 but keep NDVI value 0 (Mix), stretched to 100
    mask1 = np.greater(R,0)
    NDVI = NDVI*mask1
    
    #Free memory
    band1 = None
    band4 = None
    
    #Output NDVI
    target = "NDVI"
    otr.outputRaster(target, NDVI, time_stamp, cols, rows, geotransform, projection, metadata)
    
    #Free memory
    dataset = None
    
    
    return NDVI



def Vegetation_Classification(img, time_stamp, ndvi_threshold, img_res, cols, rows, geotransform, projection, metadata): #4/27 transfer this function to a moudle 
    #NDVI Calculation (2010NDVI, 2012NDVI, 2014NDVI, 2016NDVI)
    NDVI = NDVI_Calculation(img, time_stamp, ndvi_threshold)
    
    #Vegetation Calculation based on obtained NDVI
    print ("Classifying Vegetation...")
    mask2 = np.greater(NDVI,ndvi_threshold) #Create a mask for vegetation classification based on given ndvi threshold
    VEG = NDVI*mask2
    
    NDVI = None
    
    #Output VEG
    target = "VEG"
    otr.outputRaster(target, VEG, time_stamp, cols, rows, geotransform, projection, metadata)
    
    #Calculate Vegetation Coverage
    print("Calculating Vegetation Coverage and its Percentage...")
    vegCount = 0
    totalCount = cols*rows
    for r in VEG: #r = rows
        for c in r:
            if np.any(c != 0): #c = each elements in rows
                vegCount += 1 #calculate VEG pixel
    if img_res == "A":
        print(" >{} Vegetation Coverage is {} m^2".format(time_stamp,(vegCount*900))) #30*30
        print(" >{} Percentage of Vegetation Coverage is {}%\n".format(time_stamp,round((vegCount/totalCount)*100),2))
    elif img_res == "B":
        print(" >{} Vegetation Coverage is {} m^2".format(time_stamp,(vegCount))) #1*1
        print(" >{} Percentage of Vegetation Coverage is {}%\n".format(time_stamp,round((vegCount/totalCount)*100),2))
    else:
        print("Selected image spatial resolution is out of range : (")

    
    return VEG