
def get_split(innumber):
    '''with a number split the number into 4 ranges'''
    size = int(innumber/4)
    a1 = 0
    a2 = size
    b1 = a2 + 1
    b2 = size *2
    c1 = b2 +1
    c2 = size *3
    d1 = c2 +1
    d2 = innumber

    return [(a1,a2),(b1,b2),(c1,c2),(d1,d2)]


print(get_split(9))