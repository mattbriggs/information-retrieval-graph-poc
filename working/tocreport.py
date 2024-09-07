'''
pip install --upgrade py2neo

https://py2neo.org/

'''

from py2neo import Graph
import mdbutilities.mdbutilities as MU


graph = Graph("bolt://localhost:7687", auth=("neo4j", "xxxxxx"))


toc_path = "C:\\git\\ms\\azure-docs-pr\\articles\\cloud-services\\"

get_toc_cypher = 'Match (a {{ filepath : "{}" }}) --(content) Return content'.format(toc_path).replace("\\", "\\\\")
print(get_toc_cypher)

data = graph.run("{}".format(get_toc_cypher)).data()

print("Number of nodes: {}".format(len(data)))
# MU.write_text(str(data).replace("'", '"'), r"C:\git\feature\content-feature\ex-003\working\data.json")

type_count = {}
for i in data:
    ctype = i["content"].get('content_type')
    if ctype in type_count.keys():
        type_count[ctype] += 1
    else:
        type_count[ctype] = 1
print(type_count)

get_rels = 'Match p=(a {{ filepath : "{}" }}) --(content) Return relationships(p)'.format(toc_path).replace("\\", "\\\\")

rel_data = graph.run("{}".format(get_rels)).data()
# MU.write_text(str(rel_data).replace("'", '"'), r"C:\git\feature\content-feature\ex-003\working\rel_data.json")

labels = {}
for i in rel_data:
    source = i['relationships(p)'][0].relationships[0].nodes[0].get('node_id')
    source_label = i['relationships(p)'][0].relationships[0].nodes[0].get('name')
    source_type = i['relationships(p)'][0].relationships[0].nodes[0].get('content_type')
    target = i['relationships(p)'][0].relationships[0].nodes[1].get('node_id')
    target_label = i['relationships(p)'][0].relationships[0].nodes[1].get('name')
    target_type = i['relationships(p)'][0].relationships[0].nodes[1].get('content_type')

    if source not in labels.keys():
        labels[source] = "{} | {}".format(source_label, source_type)
    if target not in labels.keys():
        labels[target] = "{} | {}".format(target_label, target_type )

    print('"{}" -> "{}";'.format(source, target))

for i in labels.keys():
    print('"{}" [label="{}"]'.format(i, labels[i]))