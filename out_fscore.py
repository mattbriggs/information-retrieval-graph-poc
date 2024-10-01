import yaml
from neo4j import GraphDatabase
from collections import defaultdict

class FScoreCalculator:

    def __init__(self):
        # Initialize the Neo4j driver
        with open("working/fowler.yml", "r") as stream:
            self.credentials = yaml.safe_load(stream)
        self.driver = GraphDatabase.driver(
            self.credentials["domain"],
            auth=(self.credentials["username"], self.credentials["password"])
        )

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

    def run_query(self, term, query):
        with self.driver.session() as session:
            if "cat.name = $category" in query:
                # For queries that use the 'category' parameter
                print(f"Running query for category '{term}' with query:\n{query}")
                result = session.run(query, category=term)
            else:
                # For queries that use the 'term' parameter
                print(f"Running query for term '{term}' with query:\n{query}")
                result = session.run(query, term=term)
                
            retrieved_ids = [record["content_id"] for record in result]
            print(f"Retrieved IDs for '{term}': {retrieved_ids}")
            return retrieved_ids

    def run_tests(self, golden_queries, cypher_queries):
        results = defaultdict(dict)
        
        for term, expected_ids in golden_queries.items():
            # Use the appropriate query from the YAML file
            if term not in cypher_queries:
                print(f"Warning: No Cypher query provided for term '{term}'. Skipping.")
                continue

            # Execute the query for the current term
            retrieved_ids = self.run_query(term, cypher_queries[term])
            
            # Calculate precision, recall, and F-score
            precision, recall, f_score = self.calculate_f_score(expected_ids, retrieved_ids)
            results[term] = {
                "precision": precision,
                "recall": recall,
                "f_score": f_score,
            }
        
        return results

    def generate_report(self, results):
        with open("output/f_score_report.txt", "w") as f:
            f.write("F-Score Report for Information Retrieval System\n\n")
            for term, metrics in results.items():
                f.write(f"Term: {term}\n")
                f.write(f"  Precision: {metrics['precision']:.2f}\n")
                f.write(f"  Recall: {metrics['recall']:.2f}\n")
                f.write(f"  F-Score: {metrics['f_score']:.2f}\n\n")

# Main execution
if __name__ == "__main__":
    # Load the YAML configuration
    with open("queries.yml", "r") as stream:
        config = yaml.safe_load(stream)

    # Extract Neo4j connection details and queries
    cypher_queries = config["queries"]
    golden_queries = config["golden_queries"]

    # Create an FScoreCalculator instance
    f_score_calculator = FScoreCalculator()
    
    try:
        # Run the tests and generate the report
        results = f_score_calculator.run_tests(golden_queries, cypher_queries)
        f_score_calculator.generate_report(results)
        print("F-Score report generated: f_score_report.txt")
    finally:
        # Close the connection to Neo4j
        f_score_calculator.close()
