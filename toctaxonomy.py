import yaml
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import AgglomerativeClustering
import nltk
from neo4j import GraphDatabase


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
        """Clean term names by removing extra quotes."""
        return term_name.replace("'", "").strip()

    def get_terms_from_neo4j(self):
        """Fetch all terms from Neo4j."""
        print("Fetching terms from Neo4j...")
        with self.driver.session() as session:
            result = session.run("MATCH (t:Term) RETURN t.id AS id, t.name AS name, t.term_id AS term_id")
            terms = [(record["id"], self.clean_term_name(record["name"])) for record in result]
        print(f"Fetched {len(terms)} terms.")
        return terms

    def process_terms(self, term_names):
        """Tokenize and process terms using NLTK."""
        print("Processing terms...")
        processed_terms = [' '.join(nltk.word_tokenize(term)) for term in term_names]
        print(f"Processed {len(term_names)} terms.")
        return processed_terms

    def create_tfidf_matrix(self, processed_terms):
        """Create a TF-IDF matrix from the processed terms."""
        print("Creating TF-IDF matrix...")
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(processed_terms)
        print("TF-IDF matrix created.")
        return X

    def perform_clustering(self, tfidf_matrix, distance_threshold=1.5):
        """Perform agglomerative clustering on the TF-IDF matrix."""
        print("Performing clustering...")
        clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=distance_threshold)
        clustering.fit(tfidf_matrix.toarray())
        print(f"Clustering completed. Identified {len(set(clustering.labels_))} clusters.")
        return clustering.labels_

    def generate_category_name(self, term_ids, term_names):
        """Generate a category name based on terms in the cluster."""
        top_terms = [term_names[i] for i in term_ids[:3]]  # Get the first 3 terms as the base
        return "Category: " + ", ".join(top_terms)

    def create_category_in_neo4j(self, category_name, parent_category_id=None):
        """Create a category node in Neo4j."""
        with self.driver.session() as session:
            try:
                print(f"Attempting to create category: {category_name}")  # Log the category being created
                if parent_category_id:
                    result = session.run("""
                        MERGE (c:Category {name: $category_name})
                        WITH c
                        MATCH (p:Category {id: $parent_category_id})
                        MERGE (p)-[:HAS_CHILD]->(c)
                        RETURN c.id AS category_id
                    """, category_name=category_name, parent_category_id=parent_category_id)
                else:
                    result = session.run("""
                        MERGE (c:Category {name: $category_name})
                        RETURN c.id AS category_id
                    """, category_name=category_name)

                category_record = result.single()
                if category_record:
                    print(f"Successfully created/retrieved category: {category_name} with id {category_record['category_id']}")
                    return category_record["category_id"]
                else:
                    print(f"Failed to retrieve category id for: {category_name}")
                    return None

            except Exception as e:
                print(f"Error creating category for {category_name}: {e}")
                return None

    def link_term_to_category(self, term_id, category_id):
        """Link a term to a category in Neo4j."""
        if not category_id:
            print(f"Skipping linking for term {term_id} as category_id is None.")
            return

        with self.driver.session() as session:
            try:
                session.run("""
                    MATCH (t:Term {id: $term_id})
                    MATCH (c:Category {id: $category_id})
                    MERGE (c)-[:HAS_TERM]->(t)
                """, term_id=term_id, category_id=category_id)
                print(f"Successfully linked term {term_id} to category {category_id}.")
            except Exception as e:
                print(f"Error linking term {term_id} to category {category_id}: {e}")

    def create_hierarchy(self, category_name, subcategory_ids):
        """Link categories in a parent-child relationship."""
        if not subcategory_ids:
            return
        with self.driver.session() as session:
            for child_id in subcategory_ids:
                session.run("""
                    MATCH (p:Category {name: $category_name})
                    MATCH (c:Category {id: $child_id})
                    MERGE (p)-[:HAS_CHILD]->(c)
                """, category_name=category_name, child_id=child_id)

    def close_connection(self):
        """Close the Neo4j connection."""
        self.driver.close()

    def update_clusters_in_neo4j(self):
        """Main function to process terms, perform clustering, and update Neo4j."""
        terms = self.get_terms_from_neo4j()
        term_ids, term_names = zip(*terms)

        processed_terms = self.process_terms(term_names)
        tfidf_matrix = self.create_tfidf_matrix(processed_terms)
        labels = self.perform_clustering(tfidf_matrix)

        # Map cluster IDs to the terms within them
        cluster_map = {}
        for i, cluster_id in enumerate(labels):
            if cluster_id not in cluster_map:
                cluster_map[cluster_id] = []
            cluster_map[cluster_id].append(i)

        # Updating Neo4j with categories and relationships
        total_clusters = len(cluster_map)
        print(f"Updating Neo4j with {total_clusters} categories...")

        # Create and link categories and terms
        for cluster_id, term_indices in cluster_map.items():
            # Create a descriptive category name
            category_name = self.generate_category_name(term_indices, term_names)

            # Create category node in Neo4j
            category_id = self.create_category_in_neo4j(category_name)

            if category_id:
                # Link terms to the category
                for i, term_index in enumerate(term_indices):
                    term_id = term_ids[term_index]
                    self.link_term_to_category(term_id, category_id)
                    print(f"Linked term {i + 1}/{len(term_indices)} in cluster {cluster_id + 1}.")
            else:
                print(f"Failed to create category for cluster {cluster_id}. Skipping term linking.")

        print("Neo4j update completed.")


# Usage
if __name__ == "__main__":
    updater = Neo4jClusterUpdater("working/fowler.yml")
    updater.update_clusters_in_neo4j()  # Call the correct method
    updater.close_connection()
