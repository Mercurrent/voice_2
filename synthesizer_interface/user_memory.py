import os
import json
import sys
from synthesizer_interface.trie import Trie

class UserMemory:
    def __init__(self, memory_file='user_memory.json'):
        self.memory_file = self._get_memory_file_path(memory_file)
        self.unigram_trie = Trie()
        self.bigram_tries = {}
        self.frequency_threshold = 6
        self.load_memory()

    def _get_memory_file_path(self, filename):
        """Get path to store user memory file"""
        if getattr(sys, 'frozen', False):
            # If running as bundled app, store next to executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # If running from source, store in current directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, filename)

    def load_memory(self):
        """Load user memory from JSON file"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Load unigrams
                    for word, freq in data.get('unigrams', {}).items():
                        self.unigram_trie.insert(word, freq)
                    # Load bigrams
                    for word1, next_words in data.get('bigrams', {}).items():
                        if word1 not in self.bigram_tries:
                            self.bigram_tries[word1] = Trie()
                        for word2, freq in next_words.items():
                            self.bigram_tries[word1].insert(word2, freq)
            except Exception as e:
                print(f"Error loading user memory: {e}")

    def save_memory(self):
        """Save user memory to JSON file"""
        try:
            # Convert tries to dictionary format
            data = {
                'unigrams': {},
                'bigrams': {}
            }
            
            # Save unigrams
            words_freq = []
            self.unigram_trie._collect_words(self.unigram_trie.root, words_freq)
            for word, freq in words_freq:
                data['unigrams'][word] = freq
            
            # Save bigrams
            for word1, trie in self.bigram_tries.items():
                words_freq = []
                trie._collect_words(trie.root, words_freq)
                if words_freq:
                    data['bigrams'][word1] = {w: f for w, f in words_freq}
            
            # Save to file
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving user memory: {e}")

    def update_from_text(self, text: str):
        """Update frequencies based on input text"""
        words = text.strip().split()
        if not words:
            return
            
        # Update unigram frequencies
        for word in words:
            current_freq = 0
            words_freq = []
            self.unigram_trie._collect_words_with_prefix(self.unigram_trie.root, word, words_freq)
            if words_freq:
                current_freq = words_freq[0][1]
            self.unigram_trie.insert(word, current_freq + 1)
            
        # Update bigram frequencies
        for i in range(len(words) - 1):
            word1, word2 = words[i], words[i + 1]
            if word1 not in self.bigram_tries:
                self.bigram_tries[word1] = Trie()
            
            current_freq = 0
            words_freq = []
            self.bigram_tries[word1]._collect_words_with_prefix(
                self.bigram_tries[word1].root, word2, words_freq)
            if words_freq:
                current_freq = words_freq[0][1]
            self.bigram_tries[word1].insert(word2, current_freq + 1)
        
        # Save changes
        self.save_memory() 