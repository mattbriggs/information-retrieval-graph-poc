'''
pip install --upgrade py2neo

https://py2neo.org/

'''

from py2neo import Graph
import mdbutilities.mdbutilities as MU


graph = Graph("bolt://localhost:7687", auth=("xxxxxxx", "xxxxxxxx"))
data = graph.run('MATCH (a {name: "Get started"}) -->(b) RETURN (a), (b);').data()

# print number of nodes
print("Number of nodes: {}".format(len(data)))

guides = graph.run('MATCH (a {name: "Get started"}) -->(b) RETURN (a), (b);').data()

guides_list = []
guides_list.append(["Name", "Path"])
for i in guides:
    nameof = i['a']['name']
    path = i['a']['filepath']
    row = [nameof, path]
    guides_list.append(row)

MU.write_csv(guides_list, "C:\\git\\feature\\content-feature\\ex-003\\working\\get-started-azure-docs-from-script.csv")