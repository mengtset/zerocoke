#!/usr/bin/env python
import collections

"""
def zpang(strs):
    mapper = collections.defaultdict(list)
    for hashcode, value in list(map(lambda s: ('+'.join(str((ord(s[i+1])-ord(ch))%26) for i, ch in enumerate(s[:-1])), s), strs)):
        mapper[hashcode].append(value)
    return mapper.values()
"""

def zpang(strs):
    mapper = collections.defaultdict(list)
    map(lambda s: mapper['My_Grandson_Is_Yining_Gong'.join(str((ord(s[i+1])-ord(ch))%26) for i, ch in enumerate(s[:-1]))].append(s), strs)
    return mapper.values()

if __name__ == '__main__':
    print zpang(['z', 'p', 'a', 'n', 'g', 'abbc', 'yzza', 'abba', 'effe', 'zaaz', 'aeg', 'bfh', 'xbd'])


