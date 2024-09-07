'''
Get the yaml files from a folder.

2022.11.17 Matt Briggs

'''

import os

def get_files(inpath):
    '''With the directory path, returns a list of yml file paths.
    '''
    outlist = []
    for (path, dirs, files) in os.walk(inpath):
        for filename in files:
            ext_index = filename.find(".")
            if filename[ext_index+1:] == "yml":
                entry = path + "\\" + filename
                outlist.append(entry)
    return outlist


def get_tocs_from_repo(pathtorepo):
    '''With a path to a repostory return a list of toc.yml.'''
    toc_paths = []
    allfiles = get_files(pathtorepo)
    for i in allfiles:
        check = i.lower()
        if check.find("toc.yml") > 0:
            toc_paths.append(i)
    return toc_paths