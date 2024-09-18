import yaml
import html
from neo4j import GraphDatabase

class Neo4jConnection:
    def __init__(self, uri, user, password):
        """Initialize connection to Neo4j"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        """Close the connection"""
        self.driver.close()

    def run_query(self, query, parameters=None):
        """Run a query against the Neo4j database"""
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.values() for record in result]

class KeywordProcessor:
    def __init__(self, connection):
        """Initialize with a Neo4j connection"""
        self.connection = connection

    def get_keywords(self):
        """Retrieve node_id and keywords from the database"""
        query = """
        MATCH (n:content)
        WHERE n.keywords IS NOT NULL AND n.node_id IS NOT NULL
        WITH n.node_id AS nodeId, split(replace(replace(n.keywords, "[&#x27;", ""), "&#x27;]", ""), ",") AS keywordList
        UNWIND keywordList AS keyword
        RETURN nodeId, trim(keyword) AS keyword;
        """
        return self.connection.run_query(query)

    def save_terms_and_create_mentions(self, terms):
        """Insert or update terms in the database, and create the MENTION relationship"""
        create_term_query = """
        MERGE (t:Term {term_id: $term_name}) 
        ON CREATE SET t.name = $term_name, t.description = "New Term Description"
        RETURN t;
        """
        
        create_mention_relationship_query = """
        MATCH (a {node_id: $node_id}), (t:Term {term_id: $term_name})
        MERGE (a)-[:MENTION]->(t)
        RETURN a, t;
        """

        with self.connection.driver.session() as session:
            for row in terms:
                node_id = row[0]
                term_name = html.unescape(row[1])
                print(f"Processing term: {term_name} for node: {node_id}")
                
                # Create or update the Term node
                session.run(create_term_query, term_name=term_name)

                # Create the MENTION relationship between the content node and the term node
                session.run(create_mention_relationship_query, node_id=node_id, term_name=term_name)

def load_credentials(file_path):
    """Load Neo4j credentials from a YAML file"""
    with open(file_path, "r") as stream:
        return yaml.safe_load(stream)

def main():
    # Load credentials
    neocred = load_credentials("working/fowler.yml")
    uri = neocred["domain"]
    user = neocred["username"]
    password = neocred["password"]

    # Establish Neo4j connection
    neo4j_conn = Neo4jConnection(uri, user, password)

    # Process keywords and create terms and relationships
    processor = KeywordProcessor(neo4j_conn)
    nested_list = processor.get_keywords()

    # Save terms and create "MENTION" relationships
    processor.save_terms_and_create_mentions(nested_list)

    # Close the connection
    neo4j_conn.close()

if __name__ == "__main__":
    main()
