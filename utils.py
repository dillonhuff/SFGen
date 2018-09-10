def has_prefix(name, prefix):
    return name[:len(prefix)] == prefix

def comma_list(strs):
    ls = ''
    for i in range(0, len(strs)):
        s = strs[i]
        ls += s
        if (i < len(strs) - 1):
            ls += ', '
        
    return ls

