import unittest
from collections import defaultdict


class Cache_Singleton:
    '''
    Proxy for cache, e.g., redis
    '''
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


class Peer(Cache_Singleton):
    '''
    Mixin using a singleton as proxy for cache as base class
    O(n^2) exponential time
    '''
    def __init__(self, N=1024):
        super().__init__()
        self.N = N
        self._peers = {}

    def isonline(self, id:str):
        if id in self._peers:
            return True
        else:
            return False

    @property
    def all_online(self):
        return list(self._peers.keys())

    def num_connected(self, id: str):
        return len(self._peers[id]['connected'])

    def set_online(self, id:str):
        '''
        id in cache represents user is online
        '''
        if id not in self._peers:
            self._peers[id] = {'connected': {*()}}  # or {*{}} or {*[]}

    def set_offline(self, id:str):
        '''
        remove id from all connected lists
        '''
        if id in self._peers:
            self._peers.pop(id, None)
            for k in self._peers:
                try:
                    self._peers[k]['connected'].remove(id)
                except ValueError:
                    pass

    def connect(self, id_from:str, id_to:str):
        if id_from == id_to:
            raise Exception('Cannot connect to self')
        if id_from in self._peers and id_to in self._peers:
            if id_to in self._peers[id_from]['connected']:
                # already connected
                return True
            if len(self._peers[id_from]['connected']) < self.N-1 and len(self._peers[id_to]['connected']) < self.N-1:
                self._peers[id_from]['connected'].append(id_to)
                self._peers[id_to]['connected'].append(id_from)
                return True
            else:
                raise Exception(f'Too many connections n > {self.N}')
        return False

    def send_msg(self, id_from:str, id_to:str, msg:str):
        if id_from == id_to:
            raise Exception('Cannot send message to self')
        if self.connect(id_from, id_to, msg):
            # send the messsage
            print(f'Sent from {id_from} to {id_to}: {msg}')



class Graph_BFS:
    '''
    Directed graph using adjacency list representation
    O(n) linear time
    '''

    def __init__(self):
        self.graph = defaultdict(list)

    def addEdge(self,u,v):
        self.graph[u].append(v)

    def BFS(self, s):
        '''
        Breadth first search
        '''
        # Mark all the vertices as not visited
        visited = [False] * (len(self.graph))

        # Create a queue for BFS
        queue = []

        # Mark the source node as
        # visited and enqueue it
        queue.append(s)
        visited[s] = True

        while queue:

            # Dequeue a vertex from
            # queue and print it
            s = queue.pop(0)
            print(s, end = " ")

            # Get all adjacent vertices of the
            # dequeued vertex s. If a adjacent
            # has not been visited, then mark it
            # visited and enqueue it
            for i in self.graph[s]:
                if visited[i] == False:
                    queue.append(i)
                    visited[i] = True


""" To use:
g = Graph()
g.addEdge(0, 1)
g.addEdge(0, 2)
g.addEdge(1, 2)
g.addEdge(2, 0)
g.addEdge(2, 3)
g.addEdge(3, 3)

print("Following is Breadth First Traversal"
                  " (starting from vertex 2)")
g.BFS(2)
"""

class Graph_Shortest_Path:
    def __init__(self, d):
        if d:
            self.graph = defaultdict(list)
        else:
            self.graph = {'A': ['B', 'C'],
                          'B': ['C', 'D'],
                          'C': ['D'],
                          'D': ['C'],
                          'E': ['F'],
                          'F': ['C']}

    def find_all_paths(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if not self.graph.has_key(start):
            return []
        paths = []
        for node in self.graph[start]:
            if node not in path:
                newpaths = find_all_paths(self.graph, node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

    def find_shortest_path_exponential(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if start not in self.graph:
            return None
        shortest = None
        for node in self.graph[start]:
            if node not in path:
                newpath = find_shortest_path(self, node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest

    # find_shortest_path(graph, 'A', 'D') # ['A', 'B', 'D']
    def find_shortest_path(self, start, end):
        '''
        linear time using BFS [Breadth First Search].
        '''
        dist = {start: [start]}
        q = deque(start)
        while len(q):
            at = q.popleft()
            for next in self.graph[at]:
                if next not in dist:
                    dist[next] = [dist[at], next]
                    q.append(next)
        return dist.get(end)


if __name__ == '__main__':
    class TestGraph(unittest.TestCase):

        def test_cache(self):
            peer = Peer()
            peer1 = Peer()
            self.assertEqual(id(peer), id(peer1), 'Should be identical objects')

        def test_online(self):
            peer = Peer()
            id = "123"
            peer.set_online(id)
            self.assertTrue(peer.isonline(id), 'Should now be online')

        def test_offline(self):
            peer = Peer()
            id = "123"
            peer.set_online(id)
            peer.set_offline(id)
            self.assertFalse(peer.isonline(id), 'Should not be online')

        def test_connect(self):
            peer = Peer()
            id_from = "123"
            id_to = "321"
            peer.set_online(id_from)
            peer.set_online(id_to)
            self.assertTrue(peer.connect(id_from, id_to), 'Should be able to connect')

        def test_connect_offline(self):
            peer = Peer()
            id_from = "123"
            id_to = "321"
            self.assertFalse(peer.connect(id_from, id_to), 'Should not be able to connect')
            peer.set_online(id_from)
            self.assertFalse(peer.connect(id_from, id_to), 'Should still not be able to connect')
            peer.set_online(id_to)
            peer.connect(id_from, id_to)
            peer.set_offline(id_to)
            self.assertFalse(id_to in peer._peers, 'Should not be online')
            self.assertFalse(id_to in peer._peers[id_from]['connected'], 'Should also not be be connected')

        def test_connect_toomany(self):
            peer = Peer()
            id_from = "abc"
            peer.set_online(id_from)
            for x in range(peer.N-1):
                id_to = str(x)
                peer.set_online(id_to)
                peer.connect(id_from, id_to)
            self.assertLess(peer.num_connected(id_from), peer.N, 'Should be less than N')

            peer.set_online(str(peer.N-1))

            with self.assertRaises(Exception) as context:
                peer.connect(id_from, str(peer.N-1))
            self.assertIn('Too many connections', str(context.exception))

            self.assertLess(peer.num_connected(id_from), peer.N, 'Should still be less than N')

    unittest.main()
