#!/usr/bin/python -tt

import time
import sys
import os  
indir = sys.argv[1]
outcsv= sys.argv[2]
if len(sys.argv) == 3 :
    print "Using station name from path, better to use field StationName from diag.json"
    outpath =outcsv.split("/")
    outlog = "/home/bbusey/working_files/global_status/qc/" + outpath[-3] + ".txt"
else:
    # preferred method so file is linkable on main diagnostics page
    outlog = "/home/bbusey/working_files/global_status/qc/" + sys.argv[3] + ".txt"

# this is going into the global status directory
#indir='/home/bbusey/working_files/barrow/intense_A/outputs'
#outcsv='/home/bbusey/working_files/barrow/intense_A/outputs/intense_A_status.csv'
baddata = 0
badstring = ""
file_names = [fn for fn in os.listdir(indir) if any([fn.endswith('csv') ])];
for fn in file_names:
    csvfile = indir+fn
 
    if os.path.exists(csvfile) : 
        try:            
            in_file_handle = open( csvfile, 'r')
            data = in_file_handle.readlines()
            in_file_handle.close()
            lastline = data[-1].rstrip()
            lastarray = lastline.split(',')
            if len(lastarray) >=1 :
                if float(lastarray[1]) == 6999:
                    baddata +=1
                    badstring+= "\n" + csvfile
        except:
            print "Problem with:  ", indir, csvfile
            sys.exit(1) 
out_file_handle = open(outcsv, 'a')
currentTime = time.strftime('"%Y-%m-%d %H:00:00"')
logline = ','.join([currentTime, str(baddata)]) + '\n'
out_file_handle.writelines(logline)
out_file_handle.close()

# next output the bad names of the sensors with bad values
out_file_handle = open(outlog, 'w')
logline = currentTime + badstring + "\n"
out_file_handle.writelines(logline)
out_file_handle.close()
