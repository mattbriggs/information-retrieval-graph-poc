import yaml
from neo4j import GraphDatabase
from collections import defaultdict

# Neo4J connection parameters
uri = "neo4j://localhost:7687"
username = "neo4j"
password = "password"

class FScoreCalculator:

    def __init__(self, uri, username, password):
        # Initialize the Neo4j driver
        with open("working/fowler.yml", "r") as stream:
          neocred = yaml.safe_load(stream)
        self.driver = GraphDatabase.driver(neocred["domain"], auth=(neocred["username"],  neocred["password"]))

    def close(self):
        # Close the driver connection
        self.driver.close()

    def calculate_f_score(self, relevant_results, retrieved_results):
        relevant_set = set(relevant_results)
        retrieved_set = set(retrieved_results)
        
        true_positives = len(relevant_set & retrieved_set)
        precision = true_positives / len(retrieved_set) if retrieved_set else 0
        recall = true_positives / len(relevant_set) if relevant_set else 0
        if precision + recall == 0:
            return 0, 0, 0
        f_score = 2 * (precision * recall) / (precision + recall)
        return precision, recall, f_score

    def run_query(self, term):
        # Cypher query to retrieve related content by term
        query = '''
        MATCH (t:Term)-[:MENTION]-(c:Content)
        WHERE t.name = $term
        RETURN c.node_id AS content_id
        '''
        with self.driver.session() as session:
            result = session.run(query, term=term)
            return [record["content_id"] for record in result]

    def run_tests(self, golden_queries):
        results = defaultdict(dict)
        
        for term, expected_ids in golden_queries.items():
            # Execute the query for the current term
            retrieved_ids = self.run_query(term)
            
            # Calculate precision, recall, and F-score
            precision, recall, f_score = self.calculate_f_score(expected_ids, retrieved_ids)
            results[term] = {
                "precision": precision,
                "recall": recall,
                "f_score": f_score,
            }
        
        return results

    def generate_report(self, results):
        with open("C:\\git\\feature\\information-retrieval-graph-poc\\f_score_report.txt", "w") as f:
            f.write("F-Score Report for Information Retrieval System\n\n")
            for term, metrics in results.items():
                f.write(f"Term: {term}\n")
                f.write(f"  Precision: {metrics['precision']:.2f}\n")
                f.write(f"  Recall: {metrics['recall']:.2f}\n")
                f.write(f"  F-Score: {metrics['f_score']:.2f}\n\n")

# Main execution
if __name__ == "__main__":
    print("Running F-Score calculation for Information Retrieval System\n")
    # Golden queries with expected results (ground truth)
    golden_queries = {
        "XCI Data Model": ["6b83810b-1ca4-4d10-bb00-32036dce3e66"],  # Ground truth content IDs
        "concessions data": ["0b9f79f1-2159-4c4c-8b02-126f155a60e0"],
    }
    
    # Create an FScoreCalculator instance
    f_score_calculator = FScoreCalculator(uri, username, password)
    
    try:
        # Run the tests and generate the report
        results = f_score_calculator.run_tests(golden_queries)
        f_score_calculator.generate_report(results)
        print("F-Score report generated: f_score_report.txt")
    finally:
        # Close the connection to Neo4j
        f_score_calculator.close()
