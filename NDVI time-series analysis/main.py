"""
Title: geog596_final_project_Jeff
Name: Jeff Yen
RedID: 821274604
Date: 04/26/2018
"""
import gdal
import time
import csv
import Libs.veg_classification as vegcal
import Libs.veg_change_detection as vegcd

start_time = time.time() #initialize computational time

def main():
##Part 1
    print("##########Part1: Reading Image Info.##########")
    gdal.driver = gdal.GetDriverByName("GTiff")

    img_res = input("Which spatial resolution of image you would like to use for NDVI time-teries change detection: (A)30m (B)1m\nPlease enter A or B...")  
    print("\nWarning: processing 1m NAIP images might take at least 1 hour")
    
    #Read required attribures: image path, time stamp, ndvi threshold
    print("\nReading image path, time stamp, and ndvi threshold...")
    with open('./Image_Info/image_info.csv', 'r') as f:
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
            print("Selected image spatial resolution is out of range : (")
            #####Add exit function to end this script
        #time stamp
        t = int(attr_list[i][2])
        time_stamp.append(t)
        #ndvi threshold
        n = float(attr_list[i][3])
        ndvi_thres.append(n)
    
    #Calculate the number of input images
    print("\nCalculating the number of input images...")
    num_img = len(img_path)
    
    #Set up global raster properties: extent, projection, geotransform, metadata, pixelWidth, and pixel Height
    print("\nSetting up global raster properties...")
    #Read input image
    dataset = gdal.Open(img_path[0], gdal.GA_ReadOnly)
    
    #Get # of rows, # of columns, # of bands, projection, metadata
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    projection = dataset.GetProjection()
    geotransform = dataset.GetGeoTransform()
    metadata = dataset.GetMetadata()
    
##Part2
    print("\n##########Part2: Vegetation Classification##########")
    #Append Vegetation Classification (2010VEG, 2012VEG, 2014VEG, 2016VEG) into a list
    vegList = []
    for i in range (num_img):
        vegList.append(vegcal.Vegetation_Classification(img_path[i], time_stamp[i], ndvi_thres[i], img_res, cols, rows, geotransform, projection, metadata))
    
##Part3
    print("\n##########Part3: Vegetation Change Detection##########")
    vegcd.veg_change_detection(vegList, num_img, time_stamp, cols, rows, geotransform, projection, metadata)

if __name__ == '__main__':
    main()


#Performance estimation
total_time = time.time() - start_time
print ("\nOverall programming perfromance at {} seconds".format(round(total_time,2)))
