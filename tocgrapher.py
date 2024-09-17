'''
Workflow for module for graphing TOCs.

2024.9.16 Matt Briggs
'''

import yaml
import threading
import datetime
import time
import logging

import tocharvestor as TH
import tocscanner as TS
import tocformats as TF
import mdbutilities as MU

TODAYSDATE = datetime.date.fromtimestamp(time.time());

TOCLIST = []



def get_split(innumber):
    '''with a number split the number into 4 ranges'''
    size = int(innumber/4)
    a1 = 0
    a2 = size
    b1 = a2 + 1
    b2 = size *2
    c1 = b2 +1
    c2 = size *3
    d1 = c2 +1
    d2 = innumber

    return [(a1,a2),(b1,b2),(c1,c2),(d1,d2)]


def parse_toc_block(index_start, index_end, outtype, outputpath):
    '''Pass a segment of the TOC.'''
    toc_seg = list(TOCLIST[index_start:index_end])
    size = len(TOCLIST)
    for count, t, in enumerate(toc_seg):
        print("{} of {} getting {}".format(count+index_start, size, t))
        graphed = TS.input_tocfile(t)
        if outtype == "neo4j":
            try:
                output = TF.create_cypher_graph(graphed)
                filename = outputpath + "{}-graph-{}.cypher".format(TODAYSDATE, count+index_start)
                MU.write_text(output, filename)
            except Exception as e:
                logging.error("Error neo4j for {} : {}\n".format(t, e))
        elif outtype == "csv":
            try:
                filename = outputpath + "{}-graph-{}.txt".format(TODAYSDATE, count+index_start)
                MU.write_text(str(graphed), filename)
                TF.create_csv_check(output, graphed, count, TODAYSDATE)
            except Exception as e:
                logging.error("Error csv for {} : {} : {}".format(t, e, graphed))
        else:
            print("You need a value for the output type.")


def main():
    '''Builds the graph by the specified output type from a list of github 
    repositories that use the DocFX/Learn.microsoft.com content type.
    Operation: Loads a config file, counts the yml files, and parses each toc 
    file and the content associated with it. Writes to a cypher database,
    or outputs graph formats to the specified file.
    
    '''
    global TOCLIST

    with open (r"jobtoc.yml", "r") as stream:
        config = yaml.load(stream, Loader=yaml.CLoader)

    outtype = config["type"].lower()
    outputpath = config["output"]

    logging.basicConfig(filename="{}{}-logs.log".format(outputpath, TODAYSDATE), level=logging.INFO)
    logging.info("Job run at: {}".format(TODAYSDATE))

    for i in config["folders"]:
        tocs = TH.get_tocs_from_repo(i["folder"])
    
    if config["limit"] == "0":
        limit = len(tocs)
    else:
        limit = config["limit"]

    TOCLIST = tocs[:int(limit)]
    l_indexes = get_split(len(TOCLIST))
    
    if len(TOCLIST) < 8:
        parse_toc_block(0, len(TOCLIST), outtype, outputpath)
    else:
        threads = []
        for i in range(4):
            print("Thread: {}".format(i))
            th = threading.Thread(target=parse_toc_block, args=(l_indexes[i][0], l_indexes[i][1], outtype, outputpath))
            th.start()
            threads.append(th)
        [th.join() for th in threads]
    
    print("Done.")
    logging.info("Finished: {}".format(time.localtime(time.time())))


if __name__ == "__main__":
    main()