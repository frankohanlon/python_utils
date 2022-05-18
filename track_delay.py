#!/usr/bin/env python

"""
This short program looks at the last time stamp for hte last data element in an input file and computes how old this data is.
Pass the time zone, the
There are also two arguments:
--infile=/path/to/filename_of_data.csv
--timezone=Etc/GMT+0    (for GMT)
--infile=/path/to/filename_of_data.csv --timezone=Etc/GMT+0
Note, the output file will be named 'delay.csv' and will be put in the same directory as /path/to/ above.
"""
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
    timezone = ''

    try:
        extraparams = sys.argv[1]
    except IndexError:
        print ("""Needs Some information to run.  Enter like this:
             $ python tb_temp_mon.py --infile=/homez/bob_ss_toughbook/working_files/ss_status/ss_current_temp.txt --outdirectory=/homez/bob_ss_toughbook/working_files/ss_status/outputs/
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
        elif cl_param[0] == '--timezone':
            try:
                timezone = cl_param[1]
            except:
                print ('did not find valid output directory, ', cl_param[0], '\n')
                sys.exit(1)
        elif cl_param[0] == '--help' :
            print ("""
                  To correctly use this python utility:
                  $ python track_delay.py --infile=/home/bbusey/working_files/data/outputs/battery.csv --timezone=Etc/GMT+0
                  """)
            sys.exit(1)



    ###################################################################################
    ##  Open the input file                                                          ##
    ###################################################################################
    try:
        ifile = open (inputfile, 'r')
        tempdata = ifile.readlines()
        ifile.close()
    except:
        print 'problem opening %s for reading (input file)' % inputfile
        sys.exit(1)
    lastline = tempdata[-1].split('\n')

    #######################################################################
    ##  Set up the output file                                           ##
    #######################################################################
    working_dir = os.path.dirname(inputfile)
    out_file_name = working_dir + '/delay.csv'
    if os.path.exists(out_file_name) :
        ofile = open( out_file_name, 'a')
    else:
        ofile = open( out_file_name, 'w')
        ofile.writelines('"TOA5","Station"\n"TIMESTAMP","Delay"\n"TS","Days"\n","Smp"\n')

    ###################################################################################
    ##  Compute data oldness                                                         ##
    ###################################################################################
    lastdata = lastline[0].split(',')
    lastdate = lastdata[0]
    (rYr, rMo, rDay, rHr, rMin, rSec) = time.strptime(lastdate, '"%Y-%m-%d %H:%M:%S"')[0:6]
    readingTime = datetime.datetime(rYr, rMo, rDay, rHr, rMin, rSec, tzinfo=pytz.timezone(timezone))
    timeDiff = datetime.datetime.now(pytz.timezone(timezone)) - readingTime
    timeDiffDays = (timeDiff.days * 86400 + timeDiff.seconds)/86400.0
    newval = '%5.2f' % (timeDiffDays)


    ###################################################################################
    ##  Output to file                                                               ##
    ###################################################################################
    currentTime = time.strftime('"%Y-%m-%d %H:00:00"',time.gmtime())
    logline = ','.join([currentTime, newval]) + '\n'
    ofile.writelines(logline)
    ofile.close()


###########################################################
# Execution Starts Here
###########################################################

if __name__ == "__main__":
    main()

#
