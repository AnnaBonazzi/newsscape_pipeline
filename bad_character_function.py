#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 16:26:20 2018

@author: anna
Find files with high percentage of junk characters
"""
import os, glob, re
def bad_characters(new_videos, new_date):
    print('\nCollecting subtitle info\n')
    #2006-12-11_0000_US_00018529_V2_VHS18_MB27_H11_JB
    ccs = []; badchar = []
    for v in new_videos:
        y = v[0:4]; m = v[5:7]; d = v[8:10]
        ccs.append('/mnt/netapp/NewsScape/Rosenthal/'+y+'/'+y+'-'+m+'/'+y+'-'+m+'-'+d+'/'+v+'.txt3')
    
    # ■ ■ ■
    count = 0
    # Updates the previous list of CC quality stats
    try:
	os.system('mv all_cc_quality* all_cc_quality_'+new_date+'.tsv')
    except:
	pass
    with open('all_cc_quality_'+new_date+'.tsv', 'a') as out:
        #out.write('file\t% bad char.\n')
        for file in ccs:
            text = ''
            all_c = 0
            bad_c = 0
            # Saves text after '|' as string
            try:
		with open(file, 'r') as f:
                	cc = f.readlines()
	    except:
		cc = ['']
            for line in cc:
                try:
                    if int(line[0:5]) > 0:
                        if not 'Type=' in line:
                            text = text + (' '+line.split('|')[-1].strip('\n'))
                except:
                    pass
            # Finds bad characters
            chars = list(text)
            bad = re.compile('[æåàÅØÉáéèìîüùúòóøÚÆ¿˘■Ññ÷]')
            for c in chars:
                all_c += 1
                reg = bad.search(c)
                if reg:
                    bad_c += 1
            
            if bad_c == 0 or all_c == 0:
		# Updates the previous list of no-CC stats
		try:
			os.system('mv no_cc_* no_cc_'+new_date+'.tsv')
		except:
			pass
                with open('no_cc_'+new_date+'.tsv', 'a') as outt:
                    outt.write(file.split('/')[-1].split('.txt3')[0]+'\n')
                
            else:
                perc = round(float(bad_c) * 100 / all_c, 2)
                count += 1
                if '000' in str(count):
                    print(count)
                try:
                    out.write(file.split('/')[-1].split('.txt3')[0]+'\t'+str(perc)+'%\n')
                    badchar.append(file.split('/')[-1].split('.txt3')[0]+'\t'+str(perc)+'%\n')
                except:
                    try:
                        out.write(file.split('/')[-1]+'\t'+str(perc)+'%\n')
                        badchar.append(file.split('/')[-1]+'\t'+str(perc)+'%\n')
                    except:
                        pass#print(file.split('/')[-1])
    return(badchar)

  
