class RouteTrieNode:
    def __init__(self, handler=None):
        self.children = {}  # path part -> RouteTrieNode
        self.handler = handler

    def insert(self, path_part):
        """Return the child node for path_part, creating it if needed."""
        if path_part not in self.children:
            self.children[path_part] = RouteTrieNode()
        return self.children[path_part]


class RouteTrie:
    def __init__(self, root_handler=None):
        self.root = RouteTrieNode(root_handler)

    def insert(self, path_parts, handler):
        """Add a path (list of parts); only its last node stores the handler."""
        node = self.root
        for part in path_parts:
            node = node.insert(part)
        node.handler = handler

    def find(self, path_parts):
        """Return the handler for path_parts, or None if there is no match."""
        node = self.root
        for part in path_parts:
            if part not in node.children:
                return None
            node = node.children[part]
        return node.handler


class Router:
    def __init__(self, root_handler, not_found_handler=None):
        self.route_trie = RouteTrie(root_handler)
        self.not_found_handler = not_found_handler

    def add_handler(self, path, handler):
        """Add a handler for a path."""
        self.route_trie.insert(self.split_path(path), handler)

    def lookup(self, path):
        """Return the handler for a path, or the not-found handler."""
        handler = self.route_trie.find(self.split_path(path))
        return handler if handler is not None else self.not_found_handler

    def split_path(self, path):
        """Split '/a/b/' into ['a', 'b']; empty parts (extra slashes) are dropped."""
        return [part for part in path.split("/") if part]


# Provided tests
router = Router("root handler", "not found handler")
router.add_handler("/home/about", "about handler")

print(router.lookup("/"))
# Expected: root handler
print(router.lookup("/home"))
# Expected: not found handler
print(router.lookup("/home/about"))
# Expected: about handler
print(router.lookup("/home/about/"))
# Expected: about handler
print(router.lookup("/home/about/me"))
# Expected: not found handler

# Edge cases
print(router.lookup(""))  # empty path is the root
# Expected: root handler
print(router.lookup("//home//about//"))  # repeated slashes
# Expected: about handler
router.add_handler("/home/about", "new about handler")  # overwrite an existing route
print(router.lookup("/home/about"))
# Expected: new about handler
print(Router("root handler").lookup("/missing"))  # no not-found handler given
# Expected: None
