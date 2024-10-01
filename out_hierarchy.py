import yaml
from neo4j import GraphDatabase

class Neo4jQuery:
    def __init__(self):
        with open("working/fowler.yml", "r") as stream:
          neocred = yaml.safe_load(stream)
        self.driver = GraphDatabase.driver(neocred["domain"], auth=(neocred["username"],  neocred["password"]))

    def close(self):
        self.driver.close()

    def get_hierarchy(self, root_id, output_file):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (root:Category {id: $root_id})-[r:HAS_CHILD*]->(category:Category)
                OPTIONAL MATCH (category)-[t:HAS_TERM]->(term:Term)
                RETURN root, category, term, r, t;
                """,
                root_id=root_id
            )
            
            # Process the result and build the hierarchy
            nodes = {}
            relationships = []
            for record in result:
                root = record["root"]
                category = record["category"]
                term = record["term"]
                category_rels = record["r"]  # category_rels will be a list for variable-length paths
                term_rel = record["t"]
                
                # Build a node dictionary based on the category ids
                if root["id"] not in nodes:
                    nodes[root["id"]] = {
                        "name": root["name"],
                        "id": root["id"],
                        "children": [],
                        "terms": []
                    }
                if category and category["id"] not in nodes:
                    nodes[category["id"]] = {
                        "name": category["name"],
                        "id": category["id"],
                        "children": [],
                        "terms": []
                    }
                
                # Add relationships for each category path
                for rel in category_rels:
                    relationships.append((rel.start_node["id"], rel.end_node["id"]))
                
                # Add term if exists
                if term:
                    nodes[category["id"]]["terms"].append(term["name"])

            # Build the hierarchy by linking the nodes based on relationships
            for start_id, end_id in relationships:
                nodes[start_id]["children"].append(nodes[end_id])

            # Write the hierarchy to a file with UTF-8 encoding
            with open(output_file, 'w', encoding='utf-8') as file:
                visited = set()  # Track visited nodes to prevent cycles
                self.write_hierarchy(nodes[root["id"]], 0, file, visited)

    def write_hierarchy(self, node, level, file, visited):
        if node['id'] in visited:
            return  # Prevent infinite recursion by skipping already visited nodes
        visited.add(node['id'])

        indent = "│   " * level
        if level == 0:
            file.write(f"Root Term: {node['name']}\n")
        else:
            file.write(f"{indent}├── Subcategory: {node['name']}\n")

        # Write terms
        for term in node['terms']:
            file.write(f"{indent}│   └── Term: {term}\n")

        # Recursively write subcategories
        for child in node['children']:
            self.write_hierarchy(child, level + 1, file, visited)

# Usage
if __name__ == "__main__":
    root_id = "7756ccb1-300c-417b-83d4-0ddfa585005c"  # Replace with your root category ID
    output_file = "C:\\git\\feature\\information-retrieval-graph-poc\\output\\hierarchy_output.txt"  # Path to the output file

    neo4j_query = Neo4jQuery()
    try:
        neo4j_query.get_hierarchy(root_id, output_file)
        print(f"Hierarchy exported to {output_file}")
    finally:
        neo4j_query.close()
