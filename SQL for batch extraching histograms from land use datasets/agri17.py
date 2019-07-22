"""
Title: geog580_final_project_Jeff
Name: Jeff Yen
Date: 11/29/2018
"""
## Import necessary Python libraries
import psycopg2
import psycopg2.errorcodes as errorcodes
import sys, os, subprocess
import time
import numpy as np
import math
import csv


## Initialize computational time
start_time = time.time()

#### Import Image Layer Stack
##print("Importing data to schema 'rasters'")
##cmd = r"raster2pgsql -I -C -s 2230 -t 100x100 I:\ImgStack16_00.tif rasters.imgstack16_00 | psql -h localhost -p 5432 -d JY -U JY_admin"
##subprocess.call(cmd, shell=True)


## Batch Importing ROIs (Shapefiles)
"""
1. Change IPv4 local connections method from med5 to trust in configuration files, named as pg_hba.conf, (C:\Program Files\PostgreSQL\9.6\data).
2. Restart the database service using Task Manager. Go to Service Tab, find and restart "postgresql -x64-9.6"
#SRID: 2230 (ft)
#Alternative: ogr2ogr
"""

## Import LU Data
RID = 25 #Total number of input LU polygons (ROIs)
by = 2016 #Band year
lu = "agri17" #LU title
##for i in range(RID): # populate i from 0 ~ 24
##        print("Importing {}_{} to schema 'vectors'".format(lu,i))
##        cmd = 'shp2pgsql -I -s 2230 C:\g580\lu\{}\{}_{}.shp vectors.{}_{} | psql -h localhost -p 5432 -d JY -U JY_admin'.format(lu,lu,i,lu,i)
##        subprocess.call(cmd, shell=True)

## Define PostGIS connection details
HOST = '127.0.0.1'
DB_NAME = 'JY'
PORT = 5432
USER_NAME = 'JY_admin'
PASSWD = 'P4geog580'

## Connect to database with error handling
def createPostgisConnection(HOST, DB_NAME, PORT, USER_NAME, PASSWD):
   try:
       connection = psycopg2.connect(database = DB_NAME, host = HOST, port = PORT, user = USER_NAME, password = PASSWD)
       print("connection to '%s'@'%s' success!" % (DB_NAME, HOST))
       return connection
   except Exception as e:
       print("connection to '%s'@'%s' failed!" % (DB_NAME, HOST))
       print(e)
       print(errorcodes.lookup(e.pgcode))

def CreateHistogramTable(lu,rid,by,bt):
        print ("Initializing histogram extraction at RID:{},BandYear:{},BandTitle:{}".format(rid,by,bt))

        ## Connect to database
        ## print ("Connecting to database")
        connection = createPostgisConnection(HOST, DB_NAME, PORT, USER_NAME, PASSWD)
        cursor = connection.cursor()
        query1 = 'set client_encoding to "UTF8"'
        query2 = 'set search_path = public, vectors, rasters, histograms'
        cursor.execute(query1)
        cursor.execute(query2)
        
		
        ## Extract histogram and restore it to table
        query7 ="""
        Create Table histograms.h{}{}{}_{} as WITH t AS (
        SELECT ST_ValueCount(ST_Union(ST_Clip(a.rast, b.geom,true)),1) AS stats
        FROM rasters.{}{} AS a, vectors.{}_{} AS b
        WHERE ST_Intersects(b.geom,a.rast))
                
        SELECT (stats).* FROM t
        ORDER BY value""".format(bt,by,lu,rid,bt,by,lu,rid)
		
        cursor.execute(query7)
		
		
	## Add two columns in histogram table
        ## Alter histogram table
        print ("Altering h{}{}{}_{}...".format(bt,by,lu,rid))
        query8 ="""
        Alter Table histograms.h{}{}{}_{}
        Add Column "Total # of Pixel" integer,
        Add Column "% of Total Pixels" float""".format(bt,by,lu,rid)

        cursor.execute(query8)

		
        ## Calculate "Total # of Pixels" and "% of Total Pixels"
	## Update ROI's histogram table
        print("Updating h{}{}{}_{} table...".format(bt,by,lu,rid))
        query9 ="""
        with t as (
        Select sum(cast(count as float)) as "Total # of Pixels"
        from histograms.h{}{}{}_{})

        Update histograms.h{}{}{}_{}
        Set "Total # of Pixel" = "Total # of Pixels",
        "% of Total Pixels" = (count*100/"Total # of Pixels")::numeric(8,3)
        from t""".format(bt,by,lu,rid,bt,by,lu,rid)
		
        cursor.execute(query9)
        
        ## Export histogram table to CSV file
        print("Exporting h{}{}{}_{} table to csv file...".format(bt,by,lu,rid))
        if bt == "nir":
                query10 =r"""
                Copy (Select * From histograms.h{}{}{}_{})
                To 'C:\g580\lu\{}\nir\h{}{}{}_{}.csv' With CSV HEADER DELIMITER ','
                """.format(bt,by,lu,rid,lu,bt,by,lu,rid)
        elif bt == "red":
                query10 =r"""
                Copy (Select * From histograms.h{}{}{}_{})
                To 'C:\g580\lu\{}\red\h{}{}{}_{}.csv' With CSV HEADER DELIMITER ','
                """.format(bt,by,lu,rid,lu,bt,by,lu,rid)
        else:
                print("Cannot export ROI's histogram table, please check bandtitle(bt) variable...")

        cursor.execute(query10)
        connection.commit()
                

def main():
   ## Create a connection to PostGIS database
   connection = createPostgisConnection(HOST, DB_NAME, PORT, USER_NAME, PASSWD)

   ## Create ROI's histogram table
   try:
       query1 = 'set client_encoding to "UTF8"'
       query2 = 'set search_path = public, histograms'
       cursor = connection.cursor()
       cursor.execute(query1)
       cursor.execute(query2)

       ## Initialize band title and band year
       bt = ["nir","red"]

##       ## Extract NIR from NAIP2016
##       query3 ="""
##       CREATE TABLE histograms.nir{} AS
##       SELECT ST_Band(rast,4) AS rast
##       FROM histograms.imgstack16_00""".format(by[0])
##       cursor.execute(query3)
##
##       ## Extract NIR from SANDAG2000
##       query4 ="""
##       CREATE TABLE histograms.nir{} AS
##       SELECT ST_Band(rast,5) AS rast
##       FROM histograms.imgstack16_00""".format(by[1])
##       cursor.execute(query4)
##
##       ## Extract R from NAIP2016
##       query5 ="""
##       CREATE TABLE histograms.red{} AS
##       SELECT ST_Band(rast,1) AS rast
##       FROM histograms.imgstack16_00""".format(by[0])
##       cursor.execute(query5)
##
##       ## Extract R from SANDAG2000
##       query6 ="""
##       CREATE TABLE histograms.red{} AS
##       SELECT ST_Band(rast,6) AS rast
##       FROM histograms.imgstack16_00""".format(by[1])
##       cursor.execute(query6)
       
       connection.commit()


##       ## Create Histogram Table Output
##       for n in range(RID):
##               for t in bt:
##                       CreateHistogramTable(lu,n,by,t)


       for t in bt:
               ## Merge all CSV files
               ## Please delete the merged output before rerun this section of code
               ## because each round of the output will stack on the first 4 csv files
               print("Merging all csv files...")

               fout=open("all{}@{}{}.csv".format(lu,t,by),"a")

               # first file:
               for line in open(r"C:\g580\lu\{}\{}\h{}{}{}_0.csv".format(lu,t,t,by,lu)):
                       fout.write(line)
               # now the rest:
               for n in range(1,RID):
                       f = open(r"C:\g580\lu\{}\{}\h{}{}{}_".format(lu,t,t,by,lu)+str(n)+".csv")
                       f.__next__() # skip the header
                       for line in f:
                               fout.write(line)
                       f.close() # not really needed
               fout.close()

               ## Import Merged CSV files to database
               print ("Importing Merged CSV files to database...")
               query11 ="""
               CREATE TABLE histograms."all{}@{}{}"
               (value INTEGER,
               count INTEGER,
               "Total # of Pixel" NUMERIC,
               "% of Total Pixels" NUMERIC
               )
               """.format(lu,t,by)
               cursor.execute(query11)
       
               query22 =r"""
               COPY histograms."all{}@{}{}"(value,count,"Total # of Pixel","% of Total Pixels")
               FROM 'C:\g580\all{}@{}{}.csv' DELIMITER ',' CSV HEADER;
               """.format(lu,t,by,lu,t,by)
               cursor.execute(query22)

               ## Generate Mean Curve for the entire sample
               ## Summarize "count", Calculate "Total # of Pixels" and "% of Total Pixels"
               ## Output the selections to csv file.
               print ("Generating Mean Curve for the entire sample...")
               query33 =r"""
               COPY (
                  With TEST as(
                     select value, sum(count) as count
                     from "all{}@{}{}"
                     group by value
                     order by value)
              
               SELECT value, count,(Select sum(count) from TEST) as "Total # of Pixels"
               ,(count*100/(Select sum(count) from TEST))::numeric(8,3) as "% of Total Pixels"
               from TEST) To 'C:\g580\mhOutput\mh{}@{}{}.csv' With CSV HEADER DELIMITER ','
               """.format(lu,t,by,lu,t,by)
               cursor.execute(query33)
               connection.commit()
       
   except Exception as e:
       connection.rollback()
       print(e)


   ## Disconnect PostGIS databaseconnection.close()
       print("connection to '%s'@'%s' was closed!" % (DB_NAME, HOST))

   ## Performance estimation
       total_time = time.time() - start_time
       print ("\nOverall query performance at {} seconds".format(round(total_time,2)))

if __name__ == '__main__':
   main()
