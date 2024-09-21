'''This scripts contains the function to convert a yaml to a touple that 
contains two arrays. [0] is an array of nodes. [1] is an array of edges.

2022.11.17 Matt Briggs
'''

from re import X
import yaml
import uuid
import html as HTML
import logging
import mdbutilities as MU
import markdownvalidator.mdhandler as MDH
import textsummary as SUM
import textwords as LEX


#utility functions

def make_set(in_iter):
    '''With an iterable, convert to a set'''
    try:
        out_set = set(list(in_iter.keys()))
        return out_set
    except Exception as e:
        return print(e)
        exit()

def escape_text(instring):
    '''Escape characters that throw issues in Cypher.'''
    out = HTML.escape(instring, quote="True")
    return out


#TOC scanner function

def input_tocfile(intocyaml):
    '''With a toc yaml file return a touple of lists that contain node dicts 
    and edge dicts'''
    with open (intocyaml, "r") as stream:
        tocdict = yaml.load(stream, Loader=yaml.CLoader)

    spot = intocyaml.lower().find("toc.yml")
    stem = intocyaml[0:spot]

    # iterator to build a graph from the yaml TOC
    rootID = str(uuid.uuid4())
    rnode = {}
    rnode["node_id"] = rootID
    rnode["node_type"] = "content"
    rnode["name"] = "root"
    rnode["content_type"] = "root"
    rnode["href"] = "None"
    rnode["filepath"] = stem

    nodes = []
    nodes.append(rnode)
    rels = []

    def process_toc(intoc, parent_node):
        '''This is a recursive function that walks the a yaml file and builds 
        a graph object as a tuple of edges and nodes. Each tuple is an array
        of dictionaries specifying the node and the edge.'''
        if type(intoc) == str:
            pass
        elif type(intoc) == list:
            for i in intoc:
                process_toc(i, parent_node)
        elif type(intoc) == dict:
            keys =  make_set(intoc)
            try:
                if "items" in keys:
                    try:
                        node = {}
                        edge = {}
                        node["node_id"] = str(uuid.uuid4())
                        node["node_type"] = "toc"
                        node["name"] = intoc["name"]
                        node["content_type"] = "None"
                        node["href"] = "None"
                        node["filepath"] = stem
                        edge["type"] = "child"
                        edge["source"] = parent_node
                        edge["target"] = node["node_id"]
                        rels.append(edge)
                        nodes.append(node)
                        parent_node = node["node_id"]
                    except:
                        node = {}
                        edge = {}
                        node["node_id"] = str(uuid.uuid4())
                        node["node_type"] = "toc"
                        node["name"] = "no name"
                        node["content_type"] = "None"
                        node["href"] = "None"
                        node["filepath"] = stem
                        edge["type"] = "child"
                        edge["source"] = parent_node
                        edge["target"] = node["node_id"]
                        rels.append(edge)
                        nodes.append(node)
                        parent_node = node["node_id"]
                    process_toc(intoc["items"], parent_node)
                elif "href" in keys:
                        node = {}
                        edge = {}
                        node["node_id"] = str(uuid.uuid4())
                        node["node_type"] = "content"
                        node["name"] = intoc["name"]
                        node["href"] = intoc["href"]
                        filepath = stem + str(intoc["href"])
                        node["filepath"] = filepath
                        if intoc["href"].find(".md") > 0:
                            try:
                                handler = MDH.MDHandler()
                                md_page = handler.get_page(filepath)
                                node["content_type"] = md_page.metadata["ms.topic"]
                                rawtext = MU.get_textfromfile(filepath)
                                node["keywords"] = LEX.get_top_ten(rawtext)
                                node["summary"] = SUM.get_summary_text(rawtext)
                            except Exception as e:
                                logging.error("Error creating topic type for {} : error: {}".format(filepath, e))
                                node["content_type"] = "Error"
                        else:
                            node["content_type"] = "None"
                        edge["type"] = "child"
                        edge["source"] = parent_node
                        edge["target"] = node["node_id"]
                        rels.append(edge)
                        nodes.append(node)
            except Exception as e:
                print("Error: {}".format(e))
    process_toc(tocdict, rnode["node_id"])

    return (nodes, rels)

def main():
    pass

if __name__ == "__main__":
    main()