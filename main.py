#!/usr/bin/env python
# coding:utf-8
'''
Author       :  ZZP
Mail         :  zhangzhaopeng@mail.nankai.edu.cn
Created Time :  2016-09-24 10:53:31

Description  :
'''


class Cluster():

    def __init__(self, entrylist, matrix):
        self.entrylist = entrylist
        self.CHA = {}
        for idx, entry in enumerate(entrylist):
            for idx2, value in enumerate(matrix[idx]):
                if(idx <= idx2):
                    u, v = entry, entrylist[idx2]
                    if(u > v):
                        u, v = v, u
                    self.CHA[(u, v)] = value
        self.clusters = {}
        for entry in self.entrylist:
            self.clusters[entry] = []

    def get_v(self, entrylist1, entry):
        value = 0.
        for entry1 in entrylist1:
            u, v = entry1, entry
            if(u > v):
                u, v = v, u
            value += self.CHA[(u, v)]
        return value / len(entrylist1)

    def get_most(self, entrylist1, entrylist2):
        values = [self.get_v(entrylist1, entry) for entry in entrylist2]
        return entrylist2[values.index(max(values))], max(values)

    def get_min(self, entrylist1, entry):
        value = 1.
        for entry1 in entrylist1:
            u, v = entry1, entry
            if(u > v):
                u, v = v, u
            if(value > self.CHA[(u, v)]):
                value = self.CHA[(u, v)]
        return value

    def merge(self, entrylist1, entrylist2, approve_alpha, alpha, reject_alpha):
        list1 = entrylist1[:]
        list2 = entrylist2[:]
        for entry1 in entrylist1:
            for entry2 in entrylist2:
                u, v = entry1, entry2
                if(u > v):
                    u, v = v, u
                if(self.CHA[(u, v)] >= approve_alpha):
                    list1.append(entry2)
                    list2.remove(entry2)
        value = alpha
        if(list2 != []):
            entry, value = self.get_most(list1, list2)
        while(value >= alpha and list2 != []):
            if(self.get_min(list1, entry) <= reject_alpha):
                break
            list1.append(entry)
            list2.remove(entry)
            if(list2 == []):
                break
            entry, value = self.get_most(list1, list2)
        return list1, list2

    def get_minCHA(self, entrylist):
        s = 1.
        for entry1 in entrylist:
            for entry2 in entrylist:
                u, v = entry1, entry2
                if(u > v):
                    u, v = v, u
                if(s > self.CHA[(u, v)]):
                    s = self.CHA[(u, v)]
        return s

    def get_start(self, entrylist):
        cluster_entrylist = []
        for entry1 in entrylist:
            s = 0.
            for entry2 in entrylist:
                u, v = entry1, entry2
                if(u > v):
                    u, v = v, u
                s += self.CHA[(u, v)]
            cluster_entrylist.append(s)
        idx = cluster_entrylist.index(max(cluster_entrylist))
        return entrylist[idx]

    def get_class(self, entrylist, approve_alpha, alpha, reject_alpha):
        '''
        与任意一个距离大于等于approve_alpha的直接合并进入class
        新的entry与已有class之间平均距离大于alpha，且没有class中的元素与新的entry之间距离小于reject_alpha，则进入class
        '''
        classes = []
        while(entrylist != []):
            class_first_entry = self.get_start(entrylist)
            entrylist.remove(class_first_entry)
            merged, entrylist = self.merge(
                [class_first_entry], entrylist, approve_alpha, alpha, reject_alpha)
            classes.append(merged)
        return classes

    def cluster_tree(self, entrylist, approve_alpha, alpha, reject_alpha, k):
        classes = self.get_class(entrylist, approve_alpha, alpha, reject_alpha)
        if(len(classes) == 1):
            pass
        else:
            for idx, cla in enumerate(classes):
                for entry in cla:
                    self.clusters[entry].append(idx + 1)
            for cla in classes:
                if(self.get_minCHA(cla) < approve_alpha and approve_alpha < 1 and len(cla) > 1):
                    approve_alpha += k
                    alpha += k
                    reject_alpha += k
                    self.cluster_tree(cla, approve_alpha,
                                      alpha, reject_alpha, k)

    def kmeans(self, approve_alpha, alpha, reject_alpha):
        entrylist = self.entrylist[:]
        return self.get_class(entrylist, approve_alpha, alpha, reject_alpha)

    def hierarchy_cluster(self, approve_alpha, alpha, reject_alpha, k):
        entrylist = self.entrylist[:]
        self.cluster_tree(entrylist, approve_alpha, alpha, reject_alpha, k)
        sorted_trees = sorted(self.clusters.iteritems(),
                              key=lambda d: d[1], reverse=False)
        return sorted_trees

if __name__ == '__main__':

    entrylist = ['a', 'b', 'c', 'd']
    matrix = [
        [1.0, 0.9, 0.5, 0.4],
        [0.9, 1.0, 0.7, 0.9],
        [0.5, 0.7, 1.0, 0.5],
        [0.4, 0.9, 0.5, 1.0]
    ]

    # 单层聚类
    clu = Cluster(entrylist, matrix)
    approve_alpha = 0.95
    alpha = 0.85
    reject_alpha = 0.65
    classes = clu.kmeans(approve_alpha, alpha, reject_alpha)
    print classes

    # tree聚类
    clu = Cluster(entrylist, matrix)
    approve_alpha = 0.75
    alpha = 0.65
    reject_alpha = 0.55
    k = 0.1
    sorted_trees = clu.hierarchy_cluster(approve_alpha, alpha, reject_alpha, k)

    for (entry, c) in sorted_trees:
        print "entry: %s, clusters: %s" % (entry, c)
