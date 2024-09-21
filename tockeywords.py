import yaml
from neo4j import GraphDatabase, exceptions

class Neo4jConnection:
    def __init__(self, uri, user, password):
        """Initialize connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()  # Verifies the connectivity at the start
        except exceptions.Neo4jError as e:
            print(f"Error connecting to Neo4j: {e}")
            raise

    def close(self):
        """Close the connection"""
        if self.driver:
            self.driver.close()

    def run_query(self, query, parameters=None):
        """Run a query against the Neo4j database"""
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                return [record.values() for record in result]
        except exceptions.Neo4jError as e:
            print(f"Error running query: {e}")
            raise

class KeywordProcessor:
    def __init__(self, connection):
        """Initialize with a Neo4j connection"""
        self.connection = connection

    def get_keywords(self):
        """Retrieve node_id and keywords from the database"""
        query = """
        MATCH (n:Content)
        WHERE n.keywords IS NOT NULL AND n.node_id IS NOT NULL
        UNWIND n.keywords as keyword
        RETURN n.node_id, keyword;
        """
        try:
            return self.connection.run_query(query)
        except exceptions.Neo4jError as e:
            print(f"Error retrieving keywords: {e}")
            return []

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
                term_name = row[1]
                print(f"Processing term: {term_name} for node: {node_id}")
                
                try:
                    # Create or update the Term node
                    session.run(create_term_query, term_name=term_name)

                    # Create the MENTION relationship between the content node and the term node
                    session.run(create_mention_relationship_query, node_id=node_id, term_name=term_name)
                except exceptions.Neo4jError as e:
                    print(f"Error saving term {term_name} or creating relationship: {e}")

def load_credentials(file_path):
    """Load Neo4j credentials from a YAML file"""
    try:
        with open(file_path, "r") as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError as e:
        print(f"Credentials file not found: {e}")
        raise
    except yaml.YAMLError as e:
        print(f"Error loading YAML file: {e}")
        raise

def main():
    # Load credentials and establish Neo4j connection
    try:
        neocred = load_credentials("working/fowler.yml")
        neo4j_conn = Neo4jConnection(neocred["domain"], neocred["username"], neocred["password"])
    except Exception as e:
        print(f"Failed to initialize Neo4j connection: {e}")
        return

    try:
        # Process keywords and create terms and relationships
        processor = KeywordProcessor(neo4j_conn)
        nested_list = processor.get_keywords()

        # Save terms and create "MENTION" relationships
        if nested_list:
            processor.save_terms_and_create_mentions(nested_list)
        else:
            print("No keywords to process.")

    except Exception as e:
        print(f"An error occurred during processing: {e}")
    finally:
        # Close the connection
        neo4j_conn.close()

if __name__ == "__main__":
    main()
