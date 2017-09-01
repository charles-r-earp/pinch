from collections import OrderedDict

class OrderedSet(OrderedDict):
    
    def __init__(self, items=[]):
        for item in items:
            self.add(item)
            
    def __repr__(self):
        s = self.__class__.__name__ + '(['
        i = 0
        for item in self:
            s += item.__repr__()
            if i < len(self) - 1:
                s += ', '
            i += 1
        s += '])'
        return s
    
    def add(self, item):
        if item not in self:
            self[item] = None
            
class Graph(OrderedDict):
    
    def __init__(self, paths=[]):
        for path in paths:
            self.add(path)
    
    def add(self, path):
        if len(path) > 0:
            branch = path[0]
            if branch not in self:
                self[branch] = Graph([path[1:]])
            else:
                self[branch].add(path[1:])
    
    def is_leaf(self):
        return len(self) == 0
                
    def paths(self, include_leaves=True):
        paths = []
        for branch, graph in self.items():
            if graph.is_leaf():
                if include_leaves:
                    paths += [[branch]]
            else:
                next_paths = []
                for path in graph.paths(include_leaves):
                    next_paths += [[branch] + path]
                if len(next_paths) == 0:
                    next_paths += [[branch]]
                paths += next_paths
        return paths
            
            
def main():
    vocab = ['a', 'b', 'ab']
    ordered_set = OrderedSet(vocab)
    print(ordered_set)
    graph = Graph(vocab)
    print(graph.paths())
    print(graph.paths(False))

if __name__ == '__main__':
    main()