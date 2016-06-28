#!/usr/bin/env python

import os
import sys
import datetime
import time
import pytz


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
        print """Needs Some information to run.  Enter like this:
             $ python 6999filler.py --infile=/home/bbusey/working_files/data/outputs/battery.csv
             """
        sys.exit(1)

    for commandlinestuff in sys.argv :
        cl_param = commandlinestuff.split('=')
        if cl_param[0] == '--infile' :
            try:
                inputfile = cl_param[1]
                if not os.path.exists(inputfile) :
                    print 'problem finding input file, ', cl_param[0], '\n'
            except:
                print 'did not find valid input file'
                sys.exit(1)
        elif cl_param[0] == '--help' :
            print """
                  To correctly use this python utility:
                  $ python 6999filler.py --infile=/home/bbusey/working_files/data/outputs/battery.csv
                  """
            sys.exit(1)



    ###################################################################################
    ##  Open the input file                                                          ##
    ###################################################################################
    try:
        ifile = open (inputfile, 'r')
        datafile = ifile.readlines()
        ifile.close()
    except:
        print 'problem opening %s for reading (input file)' % inputfile
        sys.exit(1)
    ## grab the first value from the file to initialize things
    curdata = datafile[4].split(',')
    prevdate = curdata[0]
    (rYr, rMo, rDay, rHr, rMin, rSec) = time.strptime(prevdate, '"%Y-%m-%d %H:%M:%S"')[0:6]
    pastTime = datetime.datetime(rYr, rMo, rDay, rHr, rMin, rSec)
    ## initialize output file header plus first line of data):
    output_data = datafile[:4]
    ## loop through the rest of the file looking for data gaps
    for row in datafile[4:] :
        curdata = row.split(',')
        curdate = curdata[0]
        (rYr, rMo, rDay, rHr, rMin, rSec) = time.strptime(curdate, '"%Y-%m-%d %H:%M:%S"')[0:6]
        readingTime = datetime.datetime(rYr, rMo, rDay, rHr, rMin, rSec)
        timeDiff = readingTime - pastTime
        if timeDiff.seconds >3600 :
            # data gap found.  we need to iterate until the pastTime value
            # (filled in here) is the same as the readingTime value.
            pastTime += datetime.timedelta(seconds=3600)
            timeDiff = readingTime - pastTime
            baddate = pastTime.strftime('"%Y-%m-%d %H:%M:%S"')
            baddata = baddate + ",6999\n"
            output_data.append(baddata)
            # so now need a new loop iterating on time.
            while timeDiff.seconds > 3600 :
                ## do stuff
                pastTime += datetime.timedelta(seconds=3600)
                timeDiff = readingTime - pastTime
                baddate = pastTime.strftime('"%Y-%m-%d %H:%M:%S"')
                baddata = baddate + ",6999\n"
                output_data.append(baddata)
        output_data.append(row)
        pastTime = readingTime
    output_string = ''.join(output_data)
    try:
        ofile = open (inputfile, 'w')
        datafile = ofile.writelines(output_string)
        ofile.close()
    except:
        print 'problem saving output'
        sys.exit(1)




###########################################################
# Execution Starts Here
###########################################################

if __name__ == "__main__":
    main()

#