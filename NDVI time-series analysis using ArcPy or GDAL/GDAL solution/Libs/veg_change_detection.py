import Libs.outputraster as otr

#Part3

def veg_change_detection(vegList, num_img, time_stamp, cols, rows, geotransform, projection, metadata):
    #Vegetation Coverage Change (T1, T2, T3)
    print("\nCalculating The Change of NDVI Value...")
    CN = []
    for i in range(num_img-1):
        target = "CN"
        CN.append(vegList[i+1]-vegList[i]) #Vegetation Coverage Change = T1(2012-2010), T2(2014-2012), T3(2016-2014)
        otr.outputRaster(target, CN[i],"{}".format(i+1), cols, rows, geotransform, projection, metadata)
    
    #Vegetation Coverage Change Speed
    print("\nCalculating The Speed of NDVI Value Change...")
    SNC = []
    for i in range(num_img-2):
        target = "SNC"
        SNC.append((CN[i+1]-CN[i])/(time_stamp[i+1]-time_stamp[i])) #Vegetation Coverage Change Speed = S1(T2-T1)/period(time2-time1), S2(T3-T2)/period(time3-time2)
        otr.outputRaster(target, SNC[i],"{}".format(i+1), cols, rows, geotransform, projection, metadata)   
    
    #Vegetation Coverage Change Acceleration
    print("\nCalculating The Acceleration of NDVI Value Change...")
    ANC = []
    for i in range(num_img-3):
        target = "ANC"
        ANC.append(SNC[i+1]-SNC[i]/(time_stamp[i+1]-time_stamp[i])) #Vegetation Coverage Change Speed = A1(S2-S1)/period(time2-time1)
        otr.outputRaster(target, ANC[i],"{}".format(i+1), cols, rows, geotransform, projection, metadata)
        