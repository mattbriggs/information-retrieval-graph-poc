from neo4j import GraphDatabase
from sklearn.metrics import precision_score, recall_score, f1_score

# Load Neo4j credentials
neocred = load_credentials("working/fowler.yml")
uri = neocred["domain"]
user = neocred["username"]
password = neocred["password"]
driver = GraphDatabase.driver(uri, auth=(user, password))

# Query function to get results from Neo4j
def run_cypher_query(query):
    with driver.session() as session:
        result = session.run(query)
        return [record["term"] for record in result]

# Ground truth set for comparison
# Example ground truth (the terms you expect to be retrieved)
ground_truth = {
    "Azure Stack Hub operator", 
    "Azure Resource Manager", 
    "Cloud Operator"
}

# Sample Cypher query (adjust based on your requirements)
query = """
MATCH (t:Term) 
WHERE t.name CONTAINS 'Azure'
RETURN t.name AS term
"""

# Get the results from Neo4j
retrieved_terms = set(run_cypher_query(query))

# Evaluate Precision, Recall, and F-score
# True Positives: terms that are both in the ground truth and retrieved
true_positives = ground_truth.intersection(retrieved_terms)

# False Positives: terms that are retrieved but not relevant (not in ground truth)
false_positives = retrieved_terms - ground_truth

# False Negatives: relevant terms (in ground truth) that were not retrieved
false_negatives = ground_truth - retrieved_terms

# Precision, Recall, and F1-Score calculation
precision = len(true_positives) / (len(true_positives) + len(false_positives)) if len(retrieved_terms) > 0 else 0
recall = len(true_positives) / (len(true_positives) + len(false_negatives)) if len(ground_truth) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

# Print the metrics
print(f"Precision: {precision:.2f}")
print(f"Recall: {recall:.2f}")
print(f"F1-Score: {f1:.2f}")

# Close Neo4j connection
driver.close()
