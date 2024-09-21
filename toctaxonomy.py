import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
import nltk
from neo4j import GraphDatabase
import numpy as np


class Neo4jClusterUpdater:
    def __init__(self, credentials_path):
        """Initialize the Neo4j connection and other configurations."""
        self.credentials = self.load_credentials(credentials_path)
        self.driver = GraphDatabase.driver(
            self.credentials["domain"],
            auth=(self.credentials["username"], self.credentials["password"])
        )
        nltk.download('punkt')

    @staticmethod
    def load_credentials(file_path):
        """Load Neo4j credentials from a YAML file."""
        with open(file_path, "r") as stream:
            return yaml.safe_load(stream)

    @staticmethod
    def clean_term_name(term_name):
        """Clean term names by removing extra quotes and handling None values."""
        if term_name and isinstance(term_name, str):
            return term_name.replace("'", "").strip()
        return term_name

    def get_terms_from_neo4j(self):
        """Fetch all terms from Neo4j and clean the term_id and name."""
        print("Fetching terms from Neo4j...")
        with self.driver.session() as session:
            result = session.run("MATCH (t:Term) RETURN t.id AS id, t.name AS name, t.term_id AS term_id")
            terms = []
            for record in result:
                cleaned_term_id = self.clean_term_name(record["term_id"])
                
                if cleaned_term_id:
                    terms.append((record["id"], cleaned_term_id))
        print(f"Fetched {len(terms)} valid terms.")
        return terms

    def process_terms(self, term_names):
        """Tokenize and process terms using NLTK."""
        processed_terms = [' '.join(nltk.word_tokenize(term)) for term in term_names]
        return processed_terms

    def create_tfidf_matrix(self, processed_terms):
        """Create a TF-IDF matrix from the processed terms."""
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(processed_terms)
        return X

    def perform_clustering(self, tfidf_matrix, n_clusters):
        """Perform agglomerative clustering with a set number of clusters."""
        clustering = AgglomerativeClustering(n_clusters=n_clusters)
        clustering.fit(tfidf_matrix.toarray())
        return clustering.labels_

    def recursive_clustering(self, tfidf_matrix, term_ids, term_names, max_terms_per_category=7, parent_category_id=None):
        """Recursively create categories with a max of 7 terms per category."""
        num_terms = len(term_ids)
        
        if num_terms == 0:
            print(f"No terms available for clustering under parent category {parent_category_id}. Skipping...")
            return
        
        if num_terms <= max_terms_per_category:
            # Base case: If the number of terms is 7 or less, create a category directly
            category_name = self.generate_category_name(term_ids, term_names)
            category_id = self.create_category_in_neo4j(category_name, parent_category_id)
            if category_id is None:
                print(f"Failed to create category for {category_name}")
                return

            for term in term_names:
                if term is not None:
                    self.link_term_to_category(term, category_id)
                else:
                    print(f"Skipping linking term because term_id is None.")
        else:
            # Recursive case: Perform clustering to divide terms into sub-categories
            n_clusters = max(2, num_terms // max_terms_per_category)  # Ensure at least 2 clusters
            clustering = self.perform_clustering(tfidf_matrix, n_clusters=n_clusters)
            
            cluster_map = {}
            for i, cluster_id in enumerate(clustering):
                if cluster_id not in cluster_map:
                    cluster_map[cluster_id] = []
                cluster_map[cluster_id].append(i)

            # Process each cluster recursively
            for cluster_id, indices in cluster_map.items():
                sub_term_ids = [term_ids[i] for i in indices]
                sub_term_names = [term_names[i] for i in indices]
                sub_matrix = tfidf_matrix[indices]

                # Ensure valid sub_term_ids and sub_term_names
                if sub_term_ids and sub_term_names:
                    # Generate a category for the current level
                    category_name = self.generate_category_name(indices, term_names)
                    category_id = self.create_category_in_neo4j(category_name, parent_category_id)

                    if category_id:
                        self.recursive_clustering(sub_matrix, sub_term_ids, sub_term_names, max_terms_per_category, category_id)
                    else:
                        print(f"Failed to create category {category_name}. Skipping this cluster.")
                else:
                    print(f"Empty sub-term or name list detected for cluster {cluster_id}. Skipping...")

    def generate_category_name(self, term_ids, term_names):
        """Generate a category name based on terms in the cluster."""
        if not term_ids or not term_names:  # Ensure valid indices and names
            return "Unnamed Category"
        
        # Ensure that term_ids are valid integers (no None values)
        valid_term_ids = [i for i in term_ids if i is not None]

        if not valid_term_ids:
            return "Unnamed Category"
        
        top_terms = [term_names[i] for i in valid_term_ids[:3]]  # Get the first 3 valid terms as the base
        return "Category: " + ", ".join(top_terms)

    def create_category_in_neo4j(self, category_name, parent_category_id=None):
        """Create a category node in Neo4j."""
        with self.driver.session() as session:
            if parent_category_id:
                result = session.run("""
                    MERGE (c:Category {name: $category_name})
                    ON CREATE SET c.id = randomUUID()
                    WITH c
                    MATCH (p:Category {id: $parent_category_id})
                    MERGE (p)-[:HAS_CHILD]->(c)
                    RETURN c.id AS category_id
                """, category_name=category_name, parent_category_id=parent_category_id)
            else:
                result = session.run("""
                    MERGE (c:Category {name: $category_name})
                    ON CREATE SET c.id = randomUUID()
                    RETURN c.id AS category_id
                """, category_name=category_name)

            category_record = result.single()
            return category_record["category_id"] if category_record else None

    def link_term_to_category(self, term, category_id):
        """Link a term to a category in Neo4j."""
        if not category_id or not term:
            print(f"Skipping linking for term {term} as category_id or term_id is None.")
            return
        
        with self.driver.session() as session:
            session.run("""
                MATCH (t:Term {term_id: $term})
                MATCH (c:Category {id: $category_id})
                MERGE (c)-[:HAS_TERM]->(t)
            """, term=term, category_id=category_id)

    def update_clusters_in_neo4j(self):
        """Main function to process terms, perform clustering, and update Neo4j."""
        terms = self.get_terms_from_neo4j()
        if not terms:
            print("No valid terms found. Exiting process.")
            return
        
        term_ids, term_names = zip(*terms)

        processed_terms = self.process_terms(term_names)
        tfidf_matrix = self.create_tfidf_matrix(processed_terms)

        # Start the recursive clustering process with the root category
        self.recursive_clustering(tfidf_matrix, term_ids, term_names, max_terms_per_category=7, parent_category_id=None)

    def close_connection(self):
        """Close the Neo4j connection."""
        self.driver.close()


# Usage
if __name__ == "__main__":
    updater = Neo4jClusterUpdater("working/fowler.yml")
    updater.update_clusters_in_neo4j()
    updater.close_connection()
