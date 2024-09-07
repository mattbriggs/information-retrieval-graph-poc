def make_attribute(indict):
    keys = indict.keys()
    meat = ""
    for i in keys:
        meat += "{} : '{}', ".format(i, indict[i])
    return "{{ {} }}".format(meat[:-2])

d =  {'node_id': 'b4ed950b-d875-409a-8705-f6489f3906c1', 'node_type': 'content-node', 'toc_name': 'App specific provisioning tutorials', 'content_type': 'landing-page', 'href': '../saas-apps/tutorial-list.md'}
print(make_attribute(d))