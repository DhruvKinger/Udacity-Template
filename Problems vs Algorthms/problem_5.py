class TrieNode:
    def __init__(self):
        self.is_word = False
        self.children = {}

    def insert(self, char):
        """Return the child node for char, creating it if it does not exist."""
        if char not in self.children:
            self.children[char] = TrieNode()
        return self.children[char]

    def suffixes(self, suffix=""):
        """Return every suffix below this node that completes a word."""
        results = []
        stack = [(self, suffix)]  # iterative DFS avoids recursion-depth limits
        while stack:
            node, path = stack.pop()
            if node.is_word and path:
                results.append(path)
            for char, child in node.children.items():
                stack.append((child, path + char))
        return sorted(results)  # sorted only to make output deterministic


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        """Add a word to the trie."""
        node = self.root
        for char in word:
            node = node.insert(char)
        node.is_word = True

    def find(self, prefix):
        """Return the node at the end of prefix, or None if prefix is absent."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def suffixes(self, prefix=""):
        """Return all completions of prefix (empty list if there are none)."""
        node = self.find(prefix)
        return node.suffixes() if node else []


MyTrie = Trie()
wordList = [
    "ant", "anthology", "antagonist", "antonym",
    "fun", "function", "factory",
    "trie", "trigger", "trigonometry", "tripod"
]
for word in wordList:
    MyTrie.insert(word)

# Provided-style tests
print(MyTrie.suffixes("ant"))
# Expected: ['agonist', 'hology', 'onym']
print(MyTrie.suffixes("f"))
# Expected: ['actory', 'un', 'unction']
print(MyTrie.suffixes("tri"))
# Expected: ['e', 'gger', 'gonometry', 'pod']

# Edge cases
print(MyTrie.suffixes("xyz"))  # prefix not in the trie
# Expected: []
print(MyTrie.suffixes("tripod"))  # complete word with nothing longer
# Expected: []
print(MyTrie.suffixes(""))  # empty prefix returns every word
# Expected: ['ant', 'antagonist', 'anthology', 'antonym', 'factory', 'fun', 'function', 'trie', 'trigger', 'trigonometry', 'tripod']
print(Trie().suffixes("a"))  # empty trie
# Expected: []
