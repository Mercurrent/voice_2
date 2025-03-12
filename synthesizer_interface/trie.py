class TrieNode:
    def __init__(self):
        self.children = {}  # char -> TrieNode
        self.frequency = 0  # Frequency if this node represents end of word
        self.is_end = False
        self.word = None  # Store complete word at leaf nodes

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str, frequency: int):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.frequency = frequency
        node.word = word  # Store original word (preserving case)
    
    def _collect_words_with_prefix(self, node: TrieNode, prefix: str, words_freq: list):
        """Helper function to collect all words with exact prefix match"""
        # If we're at a word end and it matches our prefix
        if node.is_end and node.word.lower().startswith(prefix.lower()):
            words_freq.append((node.word, node.frequency))
        
        # Continue searching in children
        for child in node.children.values():
            self._collect_words_with_prefix(child, prefix, words_freq)
    
    def get_top_n_prefixed(self, prefix: str, n: int) -> list:
        """Get top n words by frequency that start with prefix"""
        # Find the node corresponding to prefix
        node = self.root
        prefix = prefix.lower()
        for char in prefix:
            if char not in node.children:
                return []  # Prefix not found
            node = node.children[char]
        
        # Collect all words under this node with their frequencies
        words_freq = []
        self._collect_words(node, words_freq)
        
        # Sort by frequency and return top n words
        words_freq.sort(key=lambda x: x[1], reverse=True)
        return [word for word, _ in words_freq[:n]]
    
    def _collect_words(self, node: TrieNode, words_freq: list):
        """Helper function to collect all words under a node"""
        if node.is_end:
            words_freq.append((node.word, node.frequency))
        
        for child in node.children.values():
            self._collect_words(child, words_freq) 