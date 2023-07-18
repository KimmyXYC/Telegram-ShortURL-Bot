# -*- coding: utf-8 -*-
# @Time: 2023/3/12 10:41
# @FileName: Base.py
# @Software: PyCharm
# @GitHub: KimmyXYC
import rtoml


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


class Tool(object):

    def dictToObj(self, dict_obj):
        if not isinstance(dict_obj, dict):
            return dict_obj
        d = Dict()
        for k, v in dict_obj.items():
            d[k] = self.dictToObj(v)
        return d


class ReadConfig(object):

    def __init__(self):
        self.config = None

    def parseFile(self, paths):
        data = rtoml.load(open(paths, 'r'))
        self.config = Tool().dictToObj(data)
        return self.config
