import gdal

def outputRaster(target, img, time_stamp, cols, rows, geotransform, projection, metadata):    
    #Write Raster Output (VEG) #no need to output this
    driver = gdal.GetDriverByName("GTiff")
    if target == "NDVI":
        out_fp = "./Output/NDVI/{}NDVI.tif".format(time_stamp) # Output file path
    elif target == "VEG":
        out_fp = "./Output/VEG/{}VEG.tif".format(time_stamp) # Output file path
    elif target == "CN":
        out_fp = "./Output/CN/T{}_CN.tif".format(time_stamp) # Output file path
    elif target == "SNC":
        out_fp = "./Output/SNC/S{}_SNC.tif".format(time_stamp) # Output file path
    elif target == "ANC":
        out_fp = "./Output/ANC/A{}_ANC.tif".format(time_stamp) # Output file path
    else:
        print ("Target is out of scope!!")
    outDataset = driver.Create(out_fp, cols, rows, 1, gdal.GDT_Float32) #1 indicates the number of band
    outBand = outDataset.GetRasterBand(1) # set up which band in outDataset you wanna write in NDVI
    outBand.WriteArray(img, 0, 0)
    
    #Set background value 0 to nodata
    outBand.SetNoDataValue(0)
    
    #Geoferencing and projection of the output NDVI image
    outDataset.SetGeoTransform(geotransform)
    outDataset.SetProjection(projection)
    outDataset.SetMetadata(metadata)
    
    #Generate band statistics
    outBand.FlushCache()
    outBand.GetStatistics(0, 1)
    
    #GDAL requires to close the dataset in order to write to disk
    outDataset = None 
    
    #Free memory
    outBand = None
    
    #Format output message
    if target == "NDVI":
        print (" >Outout {}{}.tif is completed!!".format(time_stamp, target))
    elif target == "VEG":
        print (" >Outout {}{}.tif is completed!!".format(time_stamp, target))
    elif target == "CN":
        print (" >Outout T{}_CN.tif is completed!!".format(time_stamp, target))
    elif target == "SNC":
        print (" >Outout S{}_SNC.tif is completed!!".format(time_stamp, target))
    elif target == "ANC":
        print (" >Outout A{}_ANC.tif is completed!!".format(time_stamp, target))
    else:
        print ("Target is out of scope!!")