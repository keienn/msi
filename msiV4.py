import os, re
import sys
import glob
import fileinput
import shutil
import zipfile
#import rarfile 


orig_fldr =r'D:\Patterns'
new_fldr = r'D:\Patterns\Import_Pattern'

#Unzip the archives
def get_zip():
    for z in (glob.glob(os.path.join(orig_fldr,'*.zip'))): 
        with zipfile.ZipFile(z,'r') as zip_ref:
            for real in zip_ref.infolist():
                if real.filename[-1]== '/':
                    continue
                real.filename = os.path.basename(real.filename)
                zip_ref.extract(real,orig_fldr)

#Unrar the archives
#def get_rar():
#    for r in (glob.glob(os.path.join(orig_fldr,'*.rar'))): 
#        with rarfile.RarFile(r,'r') as rar_ref:
#            for realf in rar_ref.infolist():
#                if realf.filename[-1]== '/':
#                    continue
#                realf.filename = os.path.basename(realf.filename)
#                rar_ref.extract(realf,orig_fldr)
#               
#Create new folder where selections will go              
try:
    os.mkdir(new_fldr)
except:
    print ("Folder already exists!")
    sys.exit()

#Spectrum ranges
def frequencyRanges(x):
    """ Define spectrum ranges
    """
    freq = x
    if  698 <= x <= 790:
          freq = '700Mhz'
    elif  791 <= x <= 890:
          freq = '800Mhz'
    elif  891 <= x <= 960:
          freq = '900Mhz'
    elif  1427 <= x <= 1518:
          freq = '1400Mhz'
    elif  1715 <= x <= 1890:
          freq = '1800Mhz'
    elif  1891 <= x <= 2200:
          freq = '2100Mhz'
    else:
          x >= 2200
          freq = '2Ghz'
    return freq

#Spectrum usage for description    
def frequencyUses(y):
        """ Define spectrum ranges and current usage
            Simple range and corresponding description
        """
        use = y
        if  698 <= y <= 790:
               use = 'L700'
        elif  791 <= y <= 890:
               use = 'L800'
        elif  891 <= y <= 960:
               use = 'GU900'
        elif  1427 <= y <= 1518:
                use = 'SDL-LBand'
        elif  1715 <= y <= 1890:
                use = 'GL1800'
        elif  1891 <= y <= 2200:
                use = 'U2100'
        else:
                y >= 2200
                use = 'HighBands'
        return use
    
#Move files within spectrum ranges to new folder    
def filter_relevant_files(orig_fldr):
    """
    Will select files that fall within specific frequency ranges as defined 
    by the relevant regex. Takes in the folder containing the files and returns 
    a list of the selected files
    """        
    summary_files = []
    for num,filename in enumerate(glob.glob(os.path.join(orig_fldr,'*.msi')),start = 1):
    
        if re.search(('_069[8-9]|_07[0-8][0-9]|_0790'),filename):
                summary_files.append(filename)            
        elif re.search(('_079[1-9]|_08[0-8][0-9]|_0890'),filename): 
                summary_files.append(filename)
        elif re.search(('_089[1-9]|_09[0-5][0-9]|_0960'),filename):
                summary_files.append(filename)
        elif re.search(('_142[7-9]|_14[3-9][0-9]|_15[0-1][0-8]'),filename): 
                summary_files.append(filename)
        elif re.search(('_17[1-9][0-9]|_18[0-8][0-9]|_1890'),filename): 
                summary_files.append(filename)
        elif re.search(('_189[1-9]|_19[0-9][0-9]|_2[0-1][0-9][0-9]'),filename): 
                summary_files.append(filename)
        elif re.search(('_2200|_2300|_2400|_2690'),filename):        
                summary_files.append(filename)
            
    for mf in summary_files:
        shutil.move(mf, new_fldr)       
    return summary_files

# Filter files in new folder removing duplicates and redundancies
def filter_files(new_fldr):
    """
    Remove duplicated files from the selected files using various criteria to 
    reduce number of items to be processed further
    
    """
    tempfilename = []
    for n, patfile in enumerate (glob.glob(os.path.join(new_fldr,'*.msi')),start=0):
    
        if re.search('m45|M45',patfile):
            os.remove(os.path.join(new_fldr,patfile)) 
        elif re.search('_Y2',patfile):
            os.remove(os.path.join(new_fldr,patfile))
    for n, patfile in enumerate (glob.glob(os.path.join(new_fldr,'*.msi')),start=0):  
        names_pre = os.path.basename(patfile)       
        if (len(names_pre))<= 30:
            tempfilename1 = patfile[:-4]+".MSI"
            tempfilename.append(tempfilename1)    
        elif (len(names_pre))> 30: 
            tempfilename2 = patfile[:-7]+".MSI" 
            if re.search('_025T',tempfilename2):     
                tempfilename2 = str.replace(tempfilename2,'_025T','_02T')
            tempfilename.append(tempfilename2)
        os.rename(os.path.join(new_fldr,patfile),os.path.join(new_fldr,*tempfilename))
        names_post = []   
        for tempf in range(len(tempfilename)):
            tempfilename[tempf]= str(tempfilename[tempf]) 
            names_post.append(os.path.basename(tempfilename[tempf]))               
    return(names_post)                

# Determine whether electrical tilt is fixed or variable 
def get_ET_type(new_fldr):
    """
    Determine if electrical tilt is fixed or variable. Uses difference in 
    tilt values from the file names listed after filtering
    
    """
    lst_of_files = []
    for patfile in (glob.glob(os.path.join(new_fldr,'*.msi'))):
        fullname = os.path.basename(patfile)
        lst_of_files.append(fullname)
    tilt1 = re.search(r'_\d\dT',lst_of_files[0],re.IGNORECASE) 
    tilt2 = re.search(r'_\d\dT',lst_of_files[1],re.IGNORECASE) 
    if tilt1.group(0) == tilt2.group(0):
        ET = "F"
    else:
        ET = "V"                                   
    return ET
      
#Process file with new name, comment and rename it.
def change_file_name(filter_files):
    """
    Rename the files according to convention. Uses list of filtered files and 
    processes them inplace. Returns list of properly renamed files.
    """
    
    for item in filter_files(new_fldr):
        antfreq = item[-21:-17]
        anttilt = item[-7:-5]

        with fileinput.input(os.path.join(new_fldr,item),inplace=True) as f:
            for line in f:               
                line = line.strip()                        
                if fileinput.lineno() == 1:
                   antname = line[5:]
                   x = int(antfreq)
                   freq = frequencyRanges(x) 
                   newNAME = "K"+antname+"_"+freq+"_"+anttilt+get_ET_type(new_fldr)
                   line = line[:4]+" "+newNAME
                   print(line)
                elif fileinput.lineno() == 2:
                   print(line) 
                elif fileinput.lineno() == 3:
                   print(line)
                elif fileinput.lineno() == 4:
                   print(line) 
                elif fileinput.lineno() == 5:
                    y = int(antfreq)
                    use = (frequencyUses(y))
                    comment = line+": Use for "+use
                    line = comment
                    print(line)   
                    for line in f:
                        sys.stdout.write(line)                   
                    try:
                        os.rename(os.path.join(new_fldr,item),os.path.join(new_fldr,newNAME+'.msi'))                
                    except WindowsError:
                        os.remove(os.path.join(new_fldr,newNAME+'.msi'))
                        os.rename(os.path.join(new_fldr,item),os.path.join(new_fldr,newNAME+'.msi'))

##call functions in order
get_zip()
#get_rar()
filter_relevant_files(orig_fldr)
##get_ET_type(new_fldr)
#filter_files(new_fldr)
change_file_name(filter_files)


