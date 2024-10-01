# Creating Golden Questions for Cypher Queries

Golden questions help evaluate the performance of your information retrieval system. They are typically defined by identifying relevant content for a given term or query and comparing it with the retrieved results. The process involves:

## Step 1: Define the Golden Query

The golden query is a Cypher query that retrieves the relevant content IDs based on a specific term. An example format might look like:

```cypher
MATCH (t:Term)-[:MENTION]-(c:Content)
WHERE t.name = "<term>"
RETURN c.node_id AS content_id
```

This query should be executed manually first to identify the **ground truth** content IDs that represent the ideal results.

## Step 2: Create the Golden Queries in YAML Format

In the `queries.yml` file, add your golden queries under the `golden_queries` section. Use the format:

```yaml
golden_queries:
  "XCI Data Model": ["<id1>", "<id2>", "<id3>"]
  "Another Term": ["<id4>", "<id5>"]
```

Each term is paired with a list of content IDs that you expect the query to retrieve. These will be used to calculate the precision, recall, and F-Score.

## Step 3: Write the Cypher Query
Add the corresponding Cypher queries under the `queries` section of the YAML file:

```yaml
queries:
  "XCI Data Model": "MATCH (t:Term)-[:MENTION]-(c:Content) WHERE t.name = $term RETURN c.node_id AS content_id"
```

This ensures that your script can run the query dynamically based on the provided term.

## Step 4: Execute and Review Results
Run `main.py` to see how well your Cypher queries are performing against the golden questions. Review the precision, recall, and F-Score metrics in the generated `f_score_report.txt`.


# Types of Questions with Example Cypher Queries

## 1. **Basic Term Lookup Questions**
- **What content is associated with a specific term?**
  - **Example Question**: "What are the contents related to the term 'XCI Data Model'?"
  - **Example Query**:
    ```cypher
    MATCH (t:Term)-[:MENTION]-(c:Content)
    WHERE t.name = $term
    RETURN c.node_id AS content_id
    ```
  - **Golden Question Definition**: 
    ```yaml
    golden_queries:
      "XCI Data Model": ["6b83810b-1ca4-4d10-bb00-32036dce3e66"]
    ```

## 2. **Category-Based Lookup Questions**
- **What content is associated with a specific category?**
  - **Example Question**: "Which contents are associated with the category 'Data Governance'?"
  - **Example Query**:
    ```cypher
    MATCH (cat:Category)-[:HAS_TERM]->(t:Term)-[:MENTION]-(c:Content)
    WHERE cat.name = $category
    RETURN c.node_id AS content_id
    ```
  - **Golden Question Definition**:
    ```yaml
    golden_queries:
      "Data Governance": ["12345", "67890"]
    ```

## 3. **Supercategory-Based Questions**
- **What content is associated with a supercategory?**
  - Supercategories group related categories together.
  - **Example Question**: "What contents are associated with the supercategory 'Enterprise Data Management'?"
  - **Example Query**:
    ```cypher
    MATCH (scat:SuperCategory)-[:HAS_CHILD]->(cat:Category)-[:HAS_TERM]->(t:Term)-[:MENTION]-(c:Content)
    WHERE scat.name = $supercategory
    RETURN c.node_id AS content_id
    ```
  - **Golden Question Definition**:
    ```yaml
    golden_queries:
      "Enterprise Data Management": ["98765", "54321", "12345"]
    ```

## 4. **Precision-Focused Questions**
- **Does the query return exactly the relevant content items for a given term?**
  - Helps determine if the query is overly broad by returning irrelevant content.
  - **Example Question**: "For the term 'concessions data,' is only relevant content returned?"
  - **Example Query**:
    ```cypher
    MATCH (t:Term)-[:MENTION]->(c:Content)
    WHERE t.name = $term
    AND c.content_type = 'relevant'
    RETURN c.node_id AS content_id
    ```
  - **Golden Question Definition**:
    ```yaml
    golden_queries:
      "concessions data": ["0b9f79f1-2159-4c4c-8b02-126f155a60e0"]
    ```

## 5. **Recall-Focused Questions**
- **Does the query return all possible relevant items for a given term?**
  - Focuses on identifying if the query misses some relevant content.
  - **Example Question**: "Are all documents tagged as 'XCI Data Model' being retrieved?"
  - **Example Query**:
    ```cypher
    MATCH (t:Term)-[:MENTION]-(c:Content)
    WHERE t.name = $term
    RETURN c.node_id AS content_id
    ```
  - **Golden Question Definition**:
    ```yaml
    golden_queries:
      "XCI Data Model": ["6b83810b-1ca4-4d10-bb00-32036dce3e66", "09876"]
    ```

## 6. **Comparative Questions**
- **How do two different terms compare in terms of the content they retrieve?**
  - Useful for testing overlap and differentiation between related terms.
  - **Example Question**: "How does 'XCI Data Model' compare to 'Data Integration Model' in terms of shared content?"
  - **Example Query for Overlap**:
    ```cypher
    MATCH (t1:Term)-[:MENTION]-(c:Content)<-[:MENTION]-(t2:Term)
    WHERE t1.name = $term1 AND t2.name = $term2
    RETURN c.node_id AS content_id
    ```
  - **Golden Question Definition**:
    ```yaml
    golden_queries:
      "XCI vs Data Integration": ["11111", "22222"]
    ```

## 7. **Contextual Questions**
- **What content is associated with a term within a specific context?**
  - Contexts could include publication dates, content types, or other attributes.
  - **Example Question**: "What content is related to 'XCI Data Model' that was published after 2022?"
  - **Example Query**:
    ```cypher
    MATCH (t:Term)-[:MENTION]-(c:Content)
    WHERE t.name = $term AND c.publication_date > '2022-01-01'
    RETURN c.node_id AS content_id
    ```
  - **Golden Question Definition**:
    ```yaml
    golden_queries:
      "XCI Data Model - 2022+": ["78910", "12345"]
    ```

## 8. **Relationship Density Questions**
- **How many terms share a relationship with specific content?**
  - Evaluates the density and relevance of term-to-content connections.
  - **Example Question**: "How many terms are related to content with node_id '12345'?"
  - **Example Query**:
    ```cypher
    MATCH (c:Content)<-[:MENTION]-(t:Term)
    WHERE c.node_id = $node_id
    RETURN COUNT(DISTINCT t.id) AS term_count
    ```
  - **Golden Question Definition**:
    ```yaml
    golden_queries:
      "Content-12345-term-density": [5]
    ```

## 9. **Parent-Child Relationship Questions**
- **What are the direct child categories of a specific category?**
  - **Example Question**: "What are the child categories of 'Data Management'?"
  - **Example Query**:
    ```cypher
    MATCH (parent:Category)-[:HAS_CHILD]->(child:Category)
    WHERE parent.name = $category
    RETURN child.name AS child_category
    ```
  - **Golden Question Definition**:
    ```yaml
    golden_queries:
      "Data Management Children": ["Data Governance", "Data Quality"]
    ```

## 10. **Category Membership Questions**
- **Which categories does a particular content item belong to?**
  - **Example Question**: "What categories are associated with content '12345'?"
  - **Example Query**:
    ```cypher
    MATCH (c:Content)<-[:MENTION]-(t:Term)<-[:HAS_TERM]-(cat:Category)
    WHERE c.node_id = $node_id
    RETURN cat.name AS category
    ```
  - **Golden Question Definition**:
    ```yaml
    golden_queries:
      "Content-12345-Categories": ["Data Governance", "Data Quality"]
    ```

### Setting Up Golden Questions

To implement these types of questions, you can add new entries to the `queries.yml` file using this format:

```yaml
# Sample YAML configuration for the above scenarios
queries:
  "XCI Data Model": "MATCH (t:Term)-[:MENTION]-(c:Content) WHERE t.name = $term RETURN c.node_id AS content_id"
  "Data Governance": "MATCH (cat:Category)-[:HAS_TERM]->(t:Term)-[:MENTION]-(c:Content) WHERE cat.name = $category RETURN c.node_id AS content_id"
  "Enterprise Data Management": "MATCH (scat:SuperCategory)-[:HAS_CHILD]->(cat:Category)-[:HAS_TERM]->(t:Term)-[:MENTION]-(c:Content) WHERE scat.name = $supercategory RETURN c.node_id AS content_id"
  "XCI Data Model - 2022+": "MATCH (t:Term)-[:MENTION]-(c:Content) WHERE t.name = $term AND c.publication_date > '2022-01-01' RETURN c.node_id AS content_id"

golden_queries:
  "XCI Data Model": ["6b83810b-1ca4-4d10-bb00-32036dce3e66"]
  "Data Governance": ["12345", "67890"]
  "Enterprise Data Management": ["98765", "54321", "12345"]
  "XCI Data Model - 2022+": ["78910", "12345"]
```

These types of queries will help you test the nuances of your information retrieval system and ensure that your categories and supercategories are correctly organized and queried. Let me know if you need help setting up these queries in the YAML file or adjusting the script further.