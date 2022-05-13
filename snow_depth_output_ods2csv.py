#!/usr/bin/python3

import pyexcel_ods3
import arrow
import sys
# Should create a yaml for each excel filea and put it in config directory...
# like I could have in the yaml what columns to output and the header info.

spreadsheetfile = sys.argv[1]

try:
    header = pyexcel_ods3.get_data( spreadsheetfile, row_limit=15)
except:
    print("Spreadsheet not found")
    sys.exit()
line = header ["Sheet1"][0]
title = "TOA5," + line[1] + ",Table"
line = header ["Sheet1"][2]
output_fileprefix = line[4]
line = header["Sheet1"][3]
output_directory = line[4]
header = None
outfile_5min = output_directory + output_fileprefix + "_5min.csv"
outfile_60min = output_directory + output_fileprefix + "_60min.csv"
partial_data = pyexcel_ods3.get_data(spreadsheetfile, start_row=15)
outputflag = False
# probably should add the headers here:
print (outfile_5min)
# set the file header information (same for 5min and 60min):
output_data_5min = [title,
                    "TimeStamp, Snow Depth,Snow Depth: 3hr moving average, Snow Depth: 1hr moving average, Snow Depth: No Filtering,Good Quality Value Snow Depth",
                    ",centimeters,centimeters,centimeters,centimeters,centimeters",
                    "(TZ=UTC+0),Smp,Avg,Avg,Smp,Smp"]

output_data_60min = [title,
                    "TimeStamp, Snow Depth,Snow Depth: 3hr moving average, Snow Depth: 1hr moving average, Snow Depth: No Filtering,Good Quality Value Snow Depth",
                    ",centimeters,centimeters,centimeters,centimeters,centimeters",
                    "(TZ=UTC+0),Smp,Avg,Avg,Smp,Smp"]
# output format for float data in the csv:
outformat = "{val:.2f}"

# Loop through the spreadsheet and pluck out the data
for row in partial_data["Sheet1"] :
    if row[4] == "start of season" :
        outputflag = True
    if row[4] == "end of season" :
        outputflag = False
        break
    if outputflag == True :
        date_arrow = arrow.get(row[0])
        date_string = date_arrow.format('"YYYY-MM-DD HH:mm:ss"')
        time_string = date_arrow.format('mm:ss')

        try:
            snow_infil = outformat.format(val=row[7])
        except:
            snow_infil = "6999."
        try:
            snow_3hrma = outformat.format(val=row[9])
        except:
            snow_3hrma = "6999."
        try:
            snow_1hrma = outformat.format(val=row[8])
        except:
            snow_1hrma = "6999."
        try:
            sdc = outformat.format(val=row[5])
        except:
            sdc = "6999."
        try:
            q_depth = outformat.format(val=row[10])
        except:
            q_depth = "6999."

        # form final data string
        linestring = ','.join([date_string, snow_infil, snow_3hrma, snow_1hrma, sdc, q_depth])
        output_data_5min.append(linestring)

        # append hourly data at the top of each hour
        if time_string == "00:00" :
            output_data_60min.append(linestring)


###########################################
## Final Outputs to CSV
final_out_5min = "\n".join(output_data_5min)
#fh = open(outfile_5min,'w')
#fh.write(final_out_5min)
#fh.close

final_out_60min ="\n".join(output_data_60min)

fh = open(outfile_60min,'w')
fh.write(final_out_60min)
fh.close




#
