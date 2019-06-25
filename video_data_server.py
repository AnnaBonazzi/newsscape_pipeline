#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 18:27:22 2018

@author: anna
"""
import glob, re, os, sys
import datetime
# '/home/groeling/audit'
os.chdir(sys.argv[1])
tree = '/mnt/netapp/Rosenthal/'
#file_to_check = '1987-07-07_0000_US_00020002_V0_U1_M9_EG1_DB'

# Get dates of old and new video list
now = datetime.datetime.now()
yyyy = str(now.year)
mm = str(now.month)
if len(mm) < 2:
    mm = '0'+mm
dd = str(now.day)
if len(dd) < 2:
    dd = '0'+dd
new_date = yyyy+'-'+mm+'-'+dd
old_date = glob.glob('all_videos_*.txt')[0].split('_')[-1].split('.')[0]
# Prepares output file
output = 'audit_logs/'+new_date+'_all_videos_data.tsv'

# Get current video list
print('\nCollecting list of existing videos...')
all_videos = glob.glob(tree+'*/*/*/*mp4')
for i in range(0, len(all_videos)):
    all_videos[i] = all_videos[i].split('/')[-1].split('.mp4')[0]
print('Done!\n')
# Get previous video list
with open('all_videos_'+old_date+'.txt', 'r') as f:
    old_videos = f.readlines()
for i in range (0, len(old_videos)):
    old_videos[i] = old_videos[i].strip()
# Make list of newly added videos
new_videos = []
old = open('all_videos_'+old_date+'.txt', 'a')
new = open('new_videos_'+new_date+'.txt', 'w')
newfile_count = 0
for v in all_videos:
    if not v in old_videos:
        newfile_count += 1
        new_videos.append(v)
        new.write(v+'\n')
        #old.write(v+'\n') # Remember to later update this 
print(str(newfile_count)+' new files since '+old_date)    
old.close()
new.close()

# Collect all processing reports data
proc_rep = '/mnt/netapp/Rosenthal/logs/'
# Gets periodic report data
#Not used for now
print ('\nSearching periodic reports\n')
files = glob.glob(proc_rep+'*Rosenthal-periodic-report')
counter_per = 0
f_per = []
all_per = []
no_subs_per = []
for f in files:
    with open (f, 'r') as fl:
        for line in fl:
            # Collects all processed files
            all_file = re.search('(\d{4}-\d\d-\d\d_.*)', line)
            if all_file:
                all_per.append(line.strip())
            # Collects no subs files
            nosubs_per = re.search('\s(0+ *\t\d?\d:\d\d:\d\d\.\d\d)', line)
            if nosubs_per:
                no_subs_per.append(line.strip())
            # Collects failed processing files
            if 'Failed' in line:
                counter_per += 1
                filename = re.search('(\d{4}-\d\d-\d\d.*)\tFailed', line)
                f_per.append(filename.group(1))

# Gets daily report data
print ('Searching daily reports')
f_daily = []
all_daily = []
no_subs_daily = []
files = glob.glob(proc_rep+'*Rosenthal-daily-report')
counter_d = 0
counter_nosubs = 0
switch = 0
subs = 0
allfile = 0
there = 0
for f in files:
    with open (f, 'r')as fl:
        for line in fl:
            # Collects lines of processed files
            if 'completed processing on' in line:
                allfile = 1
            all_file_d = re.search('(\d{4}-\d\d-\d\d_.*)', line) 
            if all_file_d:
                if allfile == 1:
                    all_daily.append(line.strip())
            # Collects filed repair files
            if 'failed to repair' in line:
                switch = 1
                allfile = 0 # Stops collecting general processed
            if switch == 1 and 'mpg' in line:
                counter_d += 1
                f_daily.append(line.split('.mpg')[0].strip())
            # Collects files without CC
            if 'closed captions' in line:
                switch = 0 # Stops collecting failed files
                subs = 1
            if subs == 1 and 'mpg' in line:
                counter_nosubs += 1
                no_subs_daily.append(line.split('.mpg')[0].strip())
            if '~' in line or 'Summary' in line or 'All files have captions' in line:
                subs = 0 # Stops collecting missing CC files
            

# Gets size, time and name data of all files
# Size
print ('\nGetting video size data\n')
for f in new_videos:
	os.system("ls -lh "+tree+"/"+f[0:4]+"/"+f[0:4]+"-"+f[5:7]+"/*/"+f+".mp4 >> 'all_sizes_"+new_date+".txt'")
with open ('all_sizes_'+new_date+'.txt', 'r') as f:
    all_sizes = f.readlines()
sizes = []
for s in all_sizes:
    if s.split('/')[-1].split('.mp4')[0] in new_videos:
        sizes.append(s)
try:
    os.system('rm all_sizes_'+old_date+'.txt')
except:
    pass
# Timestamps
print ('\nGetting video timestamp data\n')
for f in new_videos:
	os.system("stat --printf '%n\t%y\n' "+tree+"/"+f[0:4]+"/"+f[0:4]+"-"+f[5:7]+"/*/"+f+".mp4 >> 'all_timestamps_"+new_date+".txt'")
with open ('all_timestamps_'+new_date+'.txt', 'r') as f:
    all_timest = f.readlines()
timest = []
for t in all_timest:
    if t.split('/')[-1].split('.mp4')[0] in new_videos:
        timest.append(t)
try:
    os.system('rm all_timestamps_'+old_date+'.txt')
except:
    pass

# Gathers all info for each video
stats = []
all_files = []
for index, value in enumerate(timest):
    # Gets name, date, time
    name = value.split('/')[4].split('\t')[0].split('.mp4')[0]
    date = value.split('\t')[1].split(' ')[0]
    time = value.split(' ')[1].split('.')[0]
    # Gets file size
    if 'staff  ' in sizes[index]:
        size = sizes[index].split('staff  ')[1].split(' ')[0]
    else:
        size = sizes[index].split('staff ')[1].split(' ')[0]
    stats.append((name, size, date, time))
    all_files.append(name)
    
print('Name, size and timestamp stats gathered for '+str(len(stats))+' new files\n')

#-------
 # Find errors
 # Good filename: 2006-12-15_0000_US_00018520_V13_VHS26_MB8_EB1_JP
# Catch filenames with wrong tape/VHS combination
def wrong_combination(vnum, vhs, print_error):
    # Wrong tape / vhs combination 
    v_tape = re.match('V\d\d?', vnum) 
    b_tape = re.match('B\d\d?', vnum) 
    v_rec = re.match('VHSP?\d\d?', vhs) 
    b_rec = re.match('B\d\d?', vhs) 
    if b_tape and v_rec:
        print_error.append('Bad tape/vhs pair')
        if int(date[0:4]) < 1996:
            print_error.append('Should be a Beta')
    if v_tape and b_rec:
        print_error.append('Bad tape/vhs pair')
        if  vnum == 'V' or vnum == 'V0':
            print_error.append('Should be a Beta')
        else:
            print_error.append('Should be a VHS')
    return print_error

# Get filename components/errors in correct filenames
def name_components(name, line, error_options):
    error = 0
    print_error = []
    # Separates name segments    
    # Date
    date = line.group(1)
    if int(date.split('-')[0]) < 1940 or int(date.split('-')[0]) > 2018:
        error = 2
    if int(date.split('-')[1]) > 12:
        error = 2
    if int(date.split('-')[2]) > 31:
        error = 2
    if error == 2:
        print_error.append('Bad date')
    # Barcode
    barcode = line.group(2)
    if len(barcode) != 8:
        error = 3
        if 'Archive' in barcode:
            print_error.append('No barcode')
        else:
            print_error.append('Bad barcode')
    # Vnum, Mac
    vnum = line.group(3)
    if switch== 0:
        vhs = line.group(5)
        mac = line.group(7)
    else:
        vhs = line.group(7)
        mac = line.group(5)
    # Encoder, person, BE
    enc = line.group(9)
    person = line.group(10)
    try:
        be= line.group(11).strip('_')
    except:
        be = ' '
    # Other errors
    if 'VDROP' in name:
        print_error.append('Filename error')
    # Wrong V num / VHS combination    
    print_error = wrong_combination(vnum, vhs, print_error)
    
    # Finalizes print_error
    print_error = list(set(print_error))
    for e in print_error:
        if not e in error_options:
            error_options.append(e)
    if switch == 1:
        print_error.append('Swapped VHS')
    if len(print_error) == 1:
        print_error = print_error[0]
    elif len(print_error) == 0:
        print_error = ''
    else:
        print_error = ', '.join(print_error)
    return date, barcode, vnum, vhs, mac, enc, person, be, error, print_error, error_options


# Get filename data/errors in mostly wrong filenames
def find_error(name, short, long, ok, error_options):
    # 2005-09-05_0000_US_00001303_V3_VHS3_MB3_E3_JN_BE
    print_error = [] 
    # Searches missing components
    pieces = name.split('_')
    date= ''; barcode = ''; vnum= ''; vhs = ''; mac = ''; enc = ''; person = ''; be = ''; error = ''
    
    # Deals with wrong-sized filenames
    if len(pieces) <= 8 or len(pieces) > 10:
        # Date
        if len(pieces[0]) ==10:
		date = pieces[0]
        # Barcode
        if len(pieces[3]) ==8:
		barcode = pieces[3]
	if 'Archive' in pieces[3]:
		barcode = 'Archive'
	components = [('V#', '(V|B|U)\d\d?', vnum), ('VHS#','(VHSP?|B)\d\d?', vhs), ('Mac#', 'MB?M?\d\d?', mac), ('Encoder#', '(E|H)B?\d\d?', enc), ('person','^[A-Z]{2}$', person)]
        # Checks for presence of each component
        for c in components:
            there = 0
            for p in pieces:
                reg = re.search(c[1], p)
                if reg:
                    there = 1
                    try:
			c[2] = p
		    except:
			print(c[2])
                else:
                    if c[0] == 'Encoder#':
                        reg = re.search('[A-Z]{1,2}\d\d?',p)
                        if reg:
                            there = 2
                        
            if there == 2:
                print_error.append('Bad '+c[0])
            elif there == 0:
                print_error.append('No '+c[0])
            
        if len(pieces) <= 8:
            short += 1
            print_error.append('Filename error')
        elif len(pieces) > 10:
            long += 1
            print_error.append('Filename error')
        
    # Deals with right-sized filenames
    # 2005-09-05_0000_US_00001303_V3_VHS3_MB3_E3_JN_BE
    else:
        ok += 1 
        # Date
        date = pieces[0]
        # Barcode
        barcode = pieces[3]
        if len(pieces[3]) != 8: 
            if 'Archive' in barcode:
                print_error.append('No barcode')
            else:
                print_error.append('Bad barcode')
        # V number
        vnum = pieces[4]
        res_vnum = re.match('(V|B|U)\d\d?', vnum) 
        if not res_vnum:
            print_error.append('Bad V#')
        # VHS
        vhs = pieces[5]
        mac = pieces[6]
        res_vhs = re.match('(VHSP?|B)\d\d?', vhs) 
        if not res_vhs:
            # Checks whether it's really wrong or just misplaced
            res_vhs = re.match('(VHSP?|B)\d\d?', mac)
            if res_vhs:
                print_error.append('Swapped VHS#')
            else:
                print_error.append('Bad VHS#')
        
        # Mac num
        res_mac = re.match('MB?M?\d\d?', mac)
        if not res_mac:
            res_mac = re.match('MB?M?\d\d?', vhs)
            if res_mac:
                print_error.append('Swapped Mac#')
            else:
                print_error.append('Bad Mac#')
        # Encoder
        enc = pieces[7]
        res_encoder = re.match('(E|H)B?\d\d?', enc)
        if not res_encoder:
            print_error.append('Bad Encoder#')
        # Person
        person = pieces[8]
        res_person = re.match('[A-Z]{2}', person)
        if not res_person:
            print_error.append('Bad or swapped person')
        # BE
        if len(pieces) > 9 and 'BE' in pieces[9]:
            be = 'BE'
        
        # Other errors
        if 'VDROP' in name:
            print_error.append('Filename error')
            
        print_error = wrong_combination(vnum, vhs, print_error)

    # Finalizes print_error   
    print_error = list(set(print_error))
    for e in print_error:
        if not e in error_options:
            error_options.append(e)
    if len(print_error) == 1:
        print_error = print_error[0]
    elif len(print_error) == 0:
        print_error = ''
    else:
        print_error = ', '.join(print_error) 
                 
    return date, barcode, vnum, vhs, mac, enc, person, be, error, print_error, short, long, ok, error_options

# Adjust print_error variable to include more errors
def adjust_print_error (print_error):
    if len(print_error) > 2:
        print_error = print_error + ', '
    return print_error


# MAIN -- Gathers all available data for each filename
vvm = 0
vmv = 0
all_wrong = 0
short = 0; long = 0; ok = 0
encoders = {}
bb = 0; bv = 0; vb = 0; vv = 0
error_options = []

# Variables to measure error stats
# removed

# Prepares to include % of bad/junk charaters
from bad_character_function import bad_characters
badchars = bad_characters(new_videos, new_date)

# Prepares output file
with open (output, 'w') as out:
    out.write('name\tplayer\tsize\tprocessed_date\tprocessed_time\tmissing_cc\tcc_problem\t% bad characters\tfailed_repair\tlength\twords\tdate\tbarcode\tvnum\tvhs\tmac\tencoder\tperson\tbest_effort\terrors\n')
    
# Get filename components with above functions
for index, name in enumerate(new_videos):
    failed = ' '; missing_cc = ' '; cc_problem = ' '; length = ' '; words = ' '
    name = name.split('.mp4')[0]
    # 2005-09-05_0000_US_00001303_V3_VHS3_MB3_E3_JN_BE
    struct = re.search('(\d+-\d+-\d+)_0000_US_(.*)_((V|B|U)\d\d?)_((VHSP?|B)\d\d?)_(MB?\d\d?)_((H|E)B?\d\d?)_([A-Z]{2})(_BE)?', name) 
    # 2005-09-06_0000_US_00000636_V1_MB11_VHS12_H6_DB.mp4
    wrong_struct = re.search('(\d+-\d+-\d+)_0000_US_(.*)_((V|B|U)\d\d?)_(MB?\d\d?)_((VHSP?|B)\d\d?)_((H|E)B?\d\d?)_([A-Z]{2})(_BE)?', name)
    if struct:
        vvm += 1
        switch = 0
        line = struct
    elif wrong_struct:
        vmv += 1
        switch = 1 
        line = wrong_struct
    else:
        all_wrong += 1
        switch = 2
    # Gets name parts of mostly correct names
    if switch != 2:
        date, barcode, vnum, vhs, mac, enc, person, be, error, print_error, error_options = name_components(name, line, error_options)
        
        
    # Gets specific error patterns
    else:
        date, barcode, vnum, vhs, mac, enc, person, be, error, print_error, short, long, ok, error_options = find_error(name, short, long, ok, error_options)
    
    if not 'Failed repair' in error_options:
        error_options.append('Failed repair')
    if not 'No CC' in error_options:
        error_options.append('No CC')
    if not 'CC problem' in error_options:
        error_options.append('CC problem')
    
    # Add errors from daily report
    found_d = 0
    for f in f_daily:
        if found_d == 0:
            # Failed
            if name in f:
                found_d = 1
                print_error = adjust_print_error (print_error)
                print_error = print_error + 'Failed repair'
                failed = 'failed'
    if name in no_subs_daily:
        missing_cc = 'no_cc'
        print_error = adjust_print_error (print_error)
        print_error = print_error + 'No CC'
                 
    # Add data from periodic report
    found_p = 0
    for f in all_daily:
        if found_p == 0:
            if name in f:
                found_p = 1
                # Failed
                if name in f_daily:
                    if not 'Failed repair' in print_error:
                        print_error = adjust_print_error (print_error)
                        print_error = print_error + 'Failed repair'
                        failed = 'failed'
            
                # Missing CC
                if name in no_subs_daily:
                    if not 'No CC' in print_error:
                        print_error = adjust_print_error (print_error)
                        print_error = print_error + 'No CC'
                        missing_cc = 'no_cc'
                        
                # CC problem
                if not 'No CC' in print_error:
                    if '*' in f:
                        print_error = adjust_print_error (print_error)
                        print_error = print_error + 'CC problem'
                        cc_problem = 'cc_problem'
                # Words
                words = f.split('\t')[0].strip()
                
                # Video length
		length = f.split('\t')[1].split('.')[0]
        else:
            break
        
    # Add filesize info
    try:
	size = stats[index][1]
    except:
	print(index, name)
    
    # Add processing time info
    process_date = stats[index][2]
    time = stats[index][3]
    
    # Add bad character info
    badchar = ''
    for ch in badchars:
        if name in ch:
            badchar = ch.split('\t')[1].strip()
    
    # (MISSING) Add good words info
    
    # Prints out results
    player = 'https://tvnews.sscnet.ucla.edu/conversion_playback/?conversionplayback,'
    with open (output, 'a') as out:
	out.write(name+'\t'+player+name+'\t'+size+'\t'+process_date+'\t'+time+'\t'+missing_cc+'\t'+cc_problem+'\t'+badchar+'\t'+failed+'\t'+length+'\t'+words+'\t'+date+'\t'+barcode+'\t'+vnum+'\t'+vhs+'\t'+mac+'\t'+enc+'\t'+person+'\t'+be+'\t'+print_error+'\n')
	
        
    # Measures failure stats
    #removed
    
# Updates list of current videos
old = open('all_videos_'+old_date+'.txt', 'a')
for v in new_videos:
    old.write(v+'\n')
# Replaces list of old videos with new
os.system('scp all_videos_'+old_date+'.txt /home/groeling/audit/updated_all_videos')
os.system('mv all_videos_'+old_date+'.txt all_videos_'+new_date+'.txt')
# Moves away list of new weekly videos
os.system('mv new_videos_'+new_date+'.txt new_videos/new_videos_'+new_date+'.txt')
# Move the results in the public logs folder
os.system('scp audit_logs/'+new_date+'_all_videos_data.tsv /mnt/netapp/Rosenthal/audit_logs')
  
# Copies result into lab laptop
os.system('scp audit_logs/'+new_date+'_all_videos_data.tsv tna@fm:/Users/tna/Documents/logs')
# Sends output to the logs folder on the FileMaker server
#os.system('scp annabonazzi@ca:/home/annabonazzi/audit/audit_logs/'+new_date+'_all_videos_data.tsv /Users/anna/Google_Drive/NewsScape/audit_results')
os.system('scp audit_logs/'+new_date+'_all_videos_data.tsv temp_logs')

# Sends a copy of the output to the FileMaker-accessible folder
#os.system('scp annabonazzi@ca:/home/annabonazzi/audit/audit_logs/'+new_date+'_all_videos_data.tsv /Users/anna/Google_Drive/NewsScape/audit_results/all_videos_data.tsv') 
os.system('scp audit_logs/'+new_date+'_all_videos_data.tsv temp_logs/all_videos_data.tsv')
os.system('scp audit_logs/'+new_date+'_all_videos_data.tsv tna@fm:/Users/tna/Documents/all_videos_data.tsv')
os.system('scp audit_logs/'+new_date+'_all_videos_data.tsv tna@fm:/Library/"FileMaker\ Server"/Data/Documents/all_videos_data.tsv')

print('\nDone!\n---------\n\n')
