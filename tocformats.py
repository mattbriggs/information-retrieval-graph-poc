'''
Input Nodes and Edges as a tuple of arrays that contains dictionaries 
describing the Node and Edge attributes.

Each function produces the target output. Currently supporting:
- cypher (Neo4j)
- gremlin (CosmoDB)
- graphml (Gelphi / yEd)
- dot (GraphViz)

2022.11.18 Matt Briggs

'''

from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

import mdbutilities.mdbutilities as MU
import textsummary as SUM
import textwords as LEX

NODECOUNT = 1

def make_attribute(indict):
    keys = indict.keys()
    meat = ""
    for i in keys:
        meat += "{} : '{}', ".format(i, indict[i])
    tuna = meat.replace("\\","\\\\")
    return "{{ {} }}".format(tuna[:-2])
    
class Neo4jDB:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_element(self, cquery):
        with self.driver.session() as session:
            result = session.execute_write(self._create_and_return_greeting, cquery)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run(message)
        return result.single()[0]

def run_cypher(cypher):
    with open("marmot.txt", "r") as file:
        pylon = file.read()
    add_element = Neo4jDB("neo4j+s://9fcd5bba.databases.neo4j.io", "neo4j", pylon)
    add_element.create_element(cypher)
    add_element.close()

    # local
    # add_element = Neo4jDB("bolt://localhost:7687", "neo4j", "reb00REB")
    # add_element.create_element(cypher)
    # add_element.close()

# cypher
def create_cypher_graph(ingraph):
    global NODECOUNT
    NODECOUNT = 1
    '''With the path and file to a target directory and a mapper graph, create cypher files.'''
    nodes = create_cypher_nodes(ingraph[0])
    edges = create_cypher_edges(ingraph[1])
    output = nodes + edges
    return output


def create_cypher_nodes(nodes):
    '''Create a node:
    CREATE (TheMatrix:Movie {title:'The Matrix', released:1999, tagline:'Welcome to the Real World'})'''
    global NODECOUNT
    output = ""
    for serial, i in enumerate(nodes):
        NODECOUNT += serial
        try:
            create_node = "CREATE (n{}:content {})\nReturn (n{});".\
                format(NODECOUNT, make_attribute(i), NODECOUNT)
            run_cypher(create_node)
            output += create_node
        except Exception as e:
            logging.error("Error Creating a node: {}".format(e))
    return output


def create_cypher_edges(edges):
    '''Create an edge:
    (Keanu)-[:ACTED_IN {roles:['Neo']}]->(TheMatrix)'''
    output = ""
    for i in edges:
        try: 
            create_edge = "MATCH (a:content), (b:content) WHERE a.node_id = '{}' AND b.node_id ='{}'\n\
            CREATE (a)-[r:child]->(b)\nReturn (a), (b);".format(i["source"], i["target"]) 
            output += create_edge
            run_cypher(create_edge)
        except Exception as e:
            logging.error("Error creating an edge {}".format(e))
    return output

# gremlin
def create_gremlin_text(ingraph):
    '''With the path to a target directory and a mapper graph, create cypher files.'''
    ''' '''
    nodes = create_cypher_nodes(ingraph)
    edges = create_cypher_edges(ingraph)
    output = nodes + edges
    MU.write_text(output, target)


def create_gremlin_nodes(ingraph):
    ''' '''
    output = ""
    for i in ingraph:
        output += str(i[0])
    return output


def create_gremlin_edges(ingraph):
    ''' '''
    output = ""
    for i in ingraph:
        output += str(i[1])
    return output


# graphml
def create_graphml_text(ingraph):
    '''With the path to a target directory and a mapper graph, create cypher files.'''
    nodes = create_cypher_nodes(ingraph)
    edges = create_cypher_edges(ingraph)
    output = nodes + edges
    MU.write_text(output, target)


def create_graphml_nodes(ingraph):
    ''' '''
    output = ""
    for i in ingraph:
        output += str(i[0])
    return output



def create_graphmledges(ingraph):
    ''' '''
    output = ""
    for i in ingraph:
        output += str(i[1])
    return output


# dot (GraphViz)
def create_dot_text(ingraph):
    '''With the path to a target directory and a mapper graph, create cypher files.'''
    ''' '''
    nodes = create_dot_nodes(ingraph)
    edges = create_dot_edges(ingraph)
    output = nodes + edges
    MU.write_text(output, target)


def create_dot_nodes(ingraph):
    ''' '''
    output = ""
    for i in ingraph:
        output += str(i[0])
    return output

def create_dot_edges(ingraph):
    ''' '''
    output = ""
    for i in ingraph:
        output += str(i[1])
    return output


#CSV files
def create_csv_check(folder, graph, count, indate):
    '''With a graph tuple and count create graph outputs.'''
    nodes = make_table(graph[0])
    edges = make_table(graph[1])
    nodefile = folder + "{}-{}-nodes.csv".format(indate, count)
    edgefile = folder + "{}-{}-edges.csv".format(indate, count)
    MU.write_csv(nodes, nodefile)
    MU.write_csv(edges, edgefile)


def make_table(in_array):
    '''Take an array of dictionaries and make a table of tables'''
    out_table = []
    headers = in_array[0].keys()
    out_table.append(list(headers))
    for i in in_array:
        row = []
        for j in headers:
            row.append(i[j])
        out_table.append(row)
    return(out_table)


def main():
    print("This is a module of functions for the toc mapper.")

if __name__ == "__main__":
    main()