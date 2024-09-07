def make_attribute(indict):
    keys = indict.keys()
    meat = ""
    for i in keys:
        meat += "{} : '{}', ".format(i, indict[i])
    tuna = meat.replace("\\","\\\\")
    return "{{ {} }}".format(tuna[:-2])

first = {'node_id': 'f1a2ce15-eb4b-4b30-8ae6-a6d16b74b92f', 'node_type': 'content', 'name': 'root', 'content_type': 'root', 'href': 'None', 'filepath': 'C:\\git\\ms\\azure-docs-pr\\articles\\active-directory\\app-provisioning\\'}
NODECOUNT = 1

print(first)
print(make_attribute(first))



create_node = "CREATE (n{}:content {})\nReturn (n{});".\
format(NODECOUNT, make_attribute(first), NODECOUNT)

print(create_node)