# Information Retrieval Graph

Updated: 2024.09.30

Create an information retrieval system that who effectiveness as retrieving information can be measured.

This project will be a graph-based information retrieval system that uses Neo4J, Python, and the Natural Language Toolkit (NLTK) to map content and retrieve information. The system will focus on measuring performance using an F-score. You can find my explanation of the project and its progress for the [Hackathon 2024](docs/infromation-retrival-graph-hackathon2024.md).

## Work on pattern mining discovery using a graph

![A query in the graph](docs/media/hack24-03.png)

This exercises will load a list of repositories and crawl the repo to find 'toc.yml' objects. It then feeds each toc.yml file to a function that graphs the function. A routine then produces cypher files that can be loaded into Neo4j.

### Some notes

The output of the graphing section is format agnostic, and could accommodate different graph formats.

### Project dependencies

**markdownvalidator**: https://github.com/mattbriggs/markdown-validator. I am using this as a local package. 

### Working notes

My notes:

1. Load the toc as a dictionary.
2. Iterate over each level.
3. At each level that is a list/array,
4. Unpack the dictionaries, grab the markdown file, get the content-type and add to the dictionary.

We may need a service that categories the content by possible content type based on the rules.

 - https://neo4j.com/docs/python-manual/current/get-started/
 - http://localhost:7474/browser/

### How to use instructions (rough)

The system starts with: `tocgrapher.py`

1. Update `jobtoc.yml` with the repos.
   Here is the following example of the jobtoc.yml.
    
    ```yml
    output: "C:\\data\\tocgraphs\\"
    type: "neo4j"
    limit: 1000
    folders:
      - folder: "C:\\git\\ms\\azure-docs-pr\\articles\\"
    ```

    | Property | Value | Description |
    | --- | --- | --- |
    | output | file path (escaped virgule) | Output directory where the logs will be stored or with formats with an output, where the outputs will be placed. |
    | type | Enum | `neo4j` : will connect to a Neo4J graph database and load the graph.<br>`csv`: Qill drop each toc graph as a node/edge pair of files into the output folder. |
    | limit | number | Limits the number of TOCs. Nothing will happen if you type 0. |
    | folders | array | a list of file path (escaped virgule)s to repositories to scan for` toc.ymls`. |
2. Update `fowler.yml` with Neo4J credentials.
    Here is the following example of the `fowler.yml`.
      ```yml
      ---
      username: <username>
      password: <token>
      domain: <neo url>
      ```
3. Type:
    ```python
    tocgrapher.py
    ```
4. Type:
    ```python
    tockeywords.py
    ```
5. Type:
    ```python
    toctaxonomy.py
    ```

### Generating reports

#### out_fscore.py

This script calculates the F-score for an information retrieval system using a Neo4j database. It reads configuration data and Cypher queries from a `queries.yml` file.

##### How It Works

1. **Initialization**: Establishes a connection to the Neo4j database using the credentials.
2. **Query Execution**: Runs Cypher queries against the database based on provided terms, retrieving relevant content IDs.
3. **F-Score Calculation**: Compares the retrieved IDs with expected (golden) results to compute precision, recall, and F-score metrics.
4. **Report Generation**: Outputs a summary of the results to `f_score_report.txt`.

##### Usage

1. Prepare `fowler.yml` with Neo4j credentials.
2. Create `queries.yml` with `queries` and `golden_queries` mappings.
3. Run the script: `python script_name.py`.
4. Check the generated report at `output/f_score_report.txt`. 

Used for evaluating and fine-tuning search queries in an information retrieval system.

#### out_hierarchy.py

This script queries a Neo4j database to retrieve a hierarchical structure of categories and terms starting from a given root node, then outputs it as a formatted text file. It uses `fowler.yml` to load Neo4j credentials and connects to the database to run a Cypher query that captures category and term relationships.

##### How It Works

1. **Initialize Connection**: Establishes a connection to the Neo4j database.
2. **Query Execution**: Runs a Cypher query to retrieve categories and terms starting from the specified root ID.
3. **Hierarchy Construction**: Builds a nested structure of categories and their children, linking terms.
4. **Export to File**: Outputs the hierarchy in a readable tree format to a specified text file.

##### Usage

1. Prepare `fowler.yml` with Neo4j credentials.
2. Update the script with your `root_id` and desired `output_file` path.
3. Run the script (`python script_name.py`).
4. Check the generated hierarchy output file.

Used for visualizing category structures in Neo4j databases.

### Explanation of tocgrapher

This script is used for graphing Table of Contents (TOCs) from specified repositories. It supports multiple output formats, including **Neo4j** and **CSV**. The script processes the TOC files in parallel using multiple threads for efficiency and can handle up to four separate ranges. The primary components include reading configuration settings from a YAML file, fetching the TOC files from the repository, and creating graph representations for the TOCs.

#### **Workflow Overview**
1. **Load Configuration File (`jobtoc.yml`)**:
    - Reads settings like output type, path, and folder locations to collect TOC files.
2. **Fetch TOC Files**:
    - Collects TOC files from each folder specified in the config file.
3. **Split TOCs into Ranges**:
    - Splits the TOC list into four segments for parallel processing.
4. **Process TOCs in Parallel**:
    - Each TOC segment is processed in a separate thread. Depending on the configuration, TOCs are either written to a Neo4j database or exported as a CSV.
5. **Output the Results**:
    - Writes logs and graph outputs to the specified output directory.

#### **Modules Used**
- **`yaml`**: To parse configuration files.
- **`threading`**: To enable parallel processing.
- **`datetime`**: To handle timestamps and date formatting.
- **`logging`**: To capture runtime logs and errors.
- **`neo4j`**: To connect and write to a Neo4j database.
- **`tocharvestor`, `tocscanner`, `tocformats`, `mdbutilities`**: Custom modules for TOC parsing, file scanning, graph creation, and utilities.

#### **Function Descriptions**

##### `get_split(innumber)`
Splits a given number into four equal segments. Returns a list of 4 tuples, each indicating the start and end index of a segment.
  
- **Parameters**: 
  - `innumber` (int): The total number of items to split.
  
- **Returns**: 
  - List of tuples with start and end indices: `[(a1, a2), (b1, b2), (c1, c2), (d1, d2)]`.

##### `parse_toc_block(index_start, index_end, outtype, outputpath)`
Processes a segment of the TOC list. Converts each TOC file to a graph format and writes the output to a specified file or database.

- **Parameters**: 
  - `index_start` (int): Start index for this segment.
  - `index_end` (int): End index for this segment.
  - `outtype` (str): The output type (`neo4j` or `csv`).
  - `outputpath` (str): Path for output files.

- **Functionality**:
  - Loads the credentials for Neo4j from a YAML file.
  - Writes graph representations to Neo4j or outputs as a CSV file.

##### `main()`
The main execution point for the script. It performs the following steps:

1. **Load the `jobtoc.yml` Config File**:
   - Reads and parses the YAML config file to extract settings.
2. **Determine Output Type** (`neo4j` or `csv`).
3. **Fetch the TOC Files**:
   - Retrieves TOCs from the specified folders in the config file.
4. **Limit TOC Processing**:
   - If a limit is specified in the config file, only processes up to that number of TOCs.
5. **Process TOCs in Segments**:
   - Splits the TOC list into four segments and launches a separate thread for each segment.
6. **Logs Start and Finish Times**:
   - Records the process's start and finish times.

##### **Configuration File (`jobtoc.yml`)**
The configuration file should be structured as follows:

```yaml
type: "neo4j"          # Output type: "neo4j" or "csv"
output: "path_to_output_directory"
limit: 10              # Limit the number of TOCs to process (0 for no limit)
folders:               # List of folders containing TOCs
  - folder: "folder_path_1"
  - folder: "folder_path_2"
```

#### **Script Entry Point**
If the script is executed directly, it calls the `main()` function, which runs the entire workflow.

```python
if __name__ == "__main__":
    main()
```

#### **Sample Use Case**
- The script is ideal for processing TOCs in DocFX/Learn.microsoft.com repositories, building graph structures from TOCs, and outputting those graphs to a database or text file for further analysis.

#### **Logging and Error Handling**
- Logs are written to a file with the format: `{output_path}/{todays_date}-logs.log`.
- Errors encountered while processing TOCs are captured using `logging.error()` and output to the logs.


## Note on keys

Here's an example of what the file that contains keys file might look like, including the necessary keys for Neo4j credentials, OpenAI API key, and content context:

```yaml
# Neo4j Credentials
domain: bolt://localhost:7687
username: neo4j
password: your-neo4j-password

# OpenAI API Key
openai-key: your-openai-api-key

# Content context
content: "an Azure billing service for Microsoft."

# Root node name
rootnode: "Root node name"
```

### Breakdown:
1. **Neo4j Credentials**:
   - `domain`: Specifies the connection string to your Neo4j database.
   - `username`: Your Neo4j username.
   - `password`: Your Neo4j password.

2. **OpenAI API Key**:
   - `openai-key`: The key you use to authenticate OpenAI's API.

3. **Content**:
   - `content`: The specific context related to the subject domain (e.g., in this case, an Azure billing service for Microsoft). This will be used in the prompt to OpenAI GPT-4 to help generate more contextually appropriate category names. 
4. **Root Node Name**:
   - `rootnode`: The name of the root node in the graph.

Make sure to replace the placeholders (`your-neo4j-password`, `your-openai-api-key`) with your actual credentials and content description.

## For more information

* [Hackathon 2024](docs/information-retrieval-graph-hackathon2024.md)
* [Creating Golden Questions for Cypher Queries](docs/creating_golden_questions.md)

