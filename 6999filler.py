#!/usr/bin/env python

import os
import sys
import datetime
import time
import statistics
import pytz

def diag_filecheck(curfile) :
    """
    Quick file check to make sure this only runs on actual data rather than derivative prooducts.
    :param curfile:
    :return:
    """
    if curfile.find("datapro_runtime.csv") != -1 or curfile.find("_status.csv") !=-1 or curfile.find("delay.csv") !=-1 or curfile.find("site_process.csv") !=-1 :
        #print ('diagnostic file, exiting...')
        sys.exit(1)
    return True

def interval_update(data_list) :
    """
    After every data gap, recompute the update interval
    (for sites where that value changes from time to time depending on needs)

    :param data_list:
    :return:
    """
    diff_list = []
    for i in range(len(data_list)-1) :
        # loop through the data.
        currow = data_list[i]
        curdata = currow.split(',')
        curdate = curdata[0]
        (rYr, rMo, rDay, rHr, rMin, rSec) = time.strptime(curdate, '"%Y-%m-%d %H:%M:%S"')[0:6]
        cur_readingTime = datetime.datetime(rYr, rMo, rDay, rHr, rMin, rSec)
        next_row = data_list[i+1]
        next_data = next_row.split(',')
        next_date = next_data[0]
        (rYr, rMo, rDay, rHr, rMin, rSec) = time.strptime(next_date, '"%Y-%m-%d %H:%M:%S"')[0:6]
        next_readingTime = datetime.datetime(rYr, rMo, rDay, rHr, rMin, rSec)
        timeDiff = ( next_readingTime - cur_readingTime).total_seconds()
        #print(i, timeDiff, next_date, curdate)
        diff_list.append(timeDiff)
    new_timeDiff = statistics.mode(diff_list)
    #print(new_timeDiff, curdate, next_date)
    return new_timeDiff

def main():
    """ Main Program Body
    """
    ###################################################################################
    ##  Read in the commandline parameters                                          ##
    ###################################################################################
    inputfile = ''
    try:
        extraparams = sys.argv[1]
    except IndexError:
        print ("""Needs Some information to run.  Enter like this:
             $ python 6999filler.py --infile=/home/bbusey/working_files/data/outputs/battery.csv
             """)
        sys.exit(1)

    for commandlinestuff in sys.argv :
        cl_param = commandlinestuff.split('=')
        if cl_param[0] == '--infile' :
            try:
                inputfile = cl_param[1]
                if not os.path.exists(inputfile) :
                    print ('problem finding input file, ', cl_param[0], '\n')
            except:
                print ('did not find valid input file')
                sys.exit(1)
        elif cl_param[0] == '--help' :
            print( """
                  To correctly use this python utility:
                  $ python 6999filler.py --infile=/full_path/data/outputs/battery.csv
                  """)
            sys.exit(1)



    ###################################################################################
    ##  Open the input file                                                          ##
    ###################################################################################

    try:
        a = diag_filecheck(inputfile)
        ifile = open (inputfile, 'r')
        datafile = ifile.readlines()
        ifile.close()
    except:
        print ('problem opening %s for reading (input file)' % inputfile)
        sys.exit(1)

    ###################################################################################
    ## grab the first couple datetimes from the file to initialize the output interval variable
    ###################################################################################
    print('\n\nAnalyzing:    ', inputfile)
    curdata = datafile[4].split(',')
    nextdata = datafile[5].split(',')
    prevdate = curdata[0]
    nextdate = nextdata[0]
    try:
        (rYr, rMo, rDay, rHr, rMin, rSec) = time.strptime(prevdate, '"%Y-%m-%d %H:%M:%S"')[0:6]
    except:
        print("pandas file, no gapping to be done")
        print('could change this in the future...')
        sys.exit(1)
    pastTime = datetime.datetime(rYr, rMo, rDay, rHr, rMin, rSec)
    try:
        (rYr, rMo, rDay, rHr, rMin, rSec) = time.strptime(nextdate, '"%Y-%m-%d %H:%M:%S"')[0:6]
    except:
        print("pandas file, no gapping to be done")
        sys.exit(1)
    nextTime = datetime.datetime(rYr, rMo, rDay, rHr, rMin, rSec)
    # Right here we set the initial output interval.
    output_interval = abs((nextTime - pastTime).total_seconds())


    ###################################################################################
    ## set up data list and output list
    ###################################################################################
    ## initialize output file header plus first line of data):
    output_data = datafile[:4]
    ## loop through the rest of the file looking for data gaps
    source_data = datafile[4:]


    ###################################################################################
    ## Loop through the data list.
    ###################################################################################
    for i in range(len(source_data)) :
        row = source_data[i]
        curdata = row.split(',')
        curdate = curdata[0]
        if len(curdate) == 19:
            print("pandas file or data continuation, no gapping to be done")
            sys.exit(1)
        (rYr, rMo, rDay, rHr, rMin, rSec) = time.strptime(curdate, '"%Y-%m-%d %H:%M:%S"')[0:6]
        readingTime = datetime.datetime(rYr, rMo, rDay, rHr, rMin, rSec)
        # tricky one here:  if you just do readingTime - pastTime then it just looks at the time of day.
        #    .total_seconds() is needed to return the difference in seconds properly.
        timeDiff = (readingTime - pastTime).total_seconds()

        if int(timeDiff) > int(output_interval):
            # several potential cases here.
            # Case one: Legit gap at the output_interval hop and at the end the output_interval is the sane
            # can use original code for this.
            # case two: legit gap and then at then at the end of the bap the output_interval is something new.
            # once the series is caught up to the next reading, re-evaluate the output_interval by looking
            # at like the next n rows.  Where we need 3 in a row at a same interval to reset the output_interval?

            # case three: data logger is on and off for maintenance and there is an erratic sequence.

            # data gap found.  we need to iterate until the pastTime value
            # (filled in here) is the same as the readingTime value.
            pastTime += datetime.timedelta(seconds=output_interval)
            timeDiff = (readingTime - pastTime).total_seconds()
            baddate = pastTime.strftime('"%Y-%m-%d %H:%M:%S"')
            baddata = baddate + ",6999\n"
            output_data.append(baddata)
            # so now need a new loop iterating on time.
            while timeDiff > output_interval:
                ## fill in 6999s until next real data
                pastTime += datetime.timedelta(seconds=output_interval)
                timeDiff = (readingTime - pastTime).total_seconds()
                baddate = pastTime.strftime('"%Y-%m-%d %H:%M:%S"')
                baddata = baddate + ",6999.00\n"
                output_data.append(baddata)

            # check interval via lookahead here
            # and could prompt user if new interval is indeterminate.
            # optional look for input on new interval.
            next_interval = interval_update(source_data[i + 1:i + 12])
            if next_interval != output_interval:
                print('new interval: ', len(output_data), next_interval, output_interval, row)
                output_interval = next_interval
            else:
                print('gap:  ', gap_start, '    ', curdate)
        output_data.append(row)
        pastTime = readingTime
        gap_start = pastTime.strftime('"%Y-%m-%d %H:%M:%S"')
    ## Done looping through the data list.
    output_string = ''.join(output_data)
    try:
        ofile = open (inputfile, 'w')
        datafile = ofile.writelines(output_string)
        ofile.close()
    except:
        print ('problem saving output')
        sys.exit(1)




###########################################################
# Execution Starts Here
###########################################################

if __name__ == "__main__":
    main()

#
