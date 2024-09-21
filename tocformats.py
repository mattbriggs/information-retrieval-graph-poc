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

import yaml
from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable

import mdbutilities as MU
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

def unpack_data(data):
    """
    Unpacks input data into node_data and edge_data.
    
    :param data: A tuple containing two lists (nodes and edges).
    :return: Two lists: node_data and edge_data.
    """
    if len(data) != 2:
        raise ValueError("Input data must contain two lists: one for nodes and one for edges.")
    
    # Unpack the data into two separate lists
    node_data = data[0]
    edge_data = data[1]
    
    # Ensure both lists are non-empty and correctly formatted
    if not isinstance(node_data, list) or not isinstance(edge_data, list):
        raise ValueError("Both nodes and edges should be provided as lists.")
    
    return node_data, edge_data

# function to handle creating nodes and edges in Neo4J
def create_cypher_graph(driver, data):
    # Use unpack_data subfunction to get nodes and edges
    node_data, edge_data = unpack_data(data)
    
    # Subfunction to create nodes
    def create_nodes(tx, node_list):
        query = """
        CREATE (n:Content {
            node_id: $node_id,
            node_type: $node_type,
            name: $name,
            content_type: $content_type,
            href: $href,
            filepath: $filepath,
            keywords: $keywords,
            summary: $summary
        })
        """
        for node in node_list:
            # Provide default values if certain keys are missing
            node.setdefault('keywords', [])
            node.setdefault('summary', '')
            tx.run(query, **node)

    # Subfunction to create relationships (edges)
    def create_relationships(tx, edge_list):
        query = """
        MATCH (a {node_id: $source}), (b {node_id: $target})
        CREATE (a)-[:CHILD_OF]->(b)
        """
        for edge in edge_list:
            tx.run(query, source=edge['source'], target=edge['target'])

    # Run the node and relationship creation in a session
    with driver.session() as session:
        # Create nodes
        session.write_transaction(create_nodes, node_data)
        
        # Create relationships
        session.write_transaction(create_relationships, edge_data)

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