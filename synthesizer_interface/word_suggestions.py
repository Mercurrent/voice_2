import os
import re

from synthesizer_interface.trie import Trie
from synthesizer_interface.utils import get_data_dir
from synthesizer_interface.user_memory import UserMemory

class WordSuggester:
    def __init__(self):
        self.unigram_trie = Trie()
        self.bigram_tries = {}  # word -> Trie
        self.user_memory = UserMemory()
        self.load_ngrams()

    def load_ngrams(self):
        """Load both unigrams and bigrams into tries"""
        data_dir = get_data_dir()
        
        self._load_unigrams(data_dir)
        self._load_bigrams(data_dir)

    def _load_unigrams(self, data_dir):
        try:
            unigrams_path = os.path.join(data_dir, 'top_10_percent_1grams.tsv')
            print(f"Loading unigrams from: {unigrams_path}")
            with open(unigrams_path, 'r', encoding='utf-8') as f:
                cnt = 0
                for line in f:
                    try:
                        word, freq = line.strip().split('\t')
                        freq = int(freq)
                        self.unigram_trie.insert(word, freq)
                        cnt += 1
                    except (ValueError, IndexError) as e:
                        print(f"Skipping malformed line: {line.strip()}")
                        cnt -= 1
                        continue
            print(f"{cnt}, Unigrams loaded into trie")
        except Exception as e:
            print(f"Error loading unigrams: {e}")
            import traceback
            traceback.print_exc()

    def _load_bigrams(self, data_dir):
        try:
            bigrams_path = os.path.join(data_dir, 'top_10_percent_2grams.tsv')
            print(f"Loading bigrams from: {bigrams_path}")
            with open(bigrams_path, 'r', encoding='utf-8') as f:
                cnt = 0
                for line in f:
                    try:
                        cnt += 1
                        words, freq = line.strip().split('\t')
                        words = words.split(' ')
                        if len(words) == 2:
                            word1, word2 = words
                            freq = int(freq)
                            if word1 not in self.bigram_tries:
                                self.bigram_tries[word1] = Trie()
                            self.bigram_tries[word1].insert(word2, freq)
                    except (ValueError, IndexError) as e:
                        cnt -= 1
                        print(f"Skipping malformed line: {line.strip()}")
                        continue
            print(f"{cnt}, Bigrams loaded into {len(self.bigram_tries)} tries")
        except Exception as e:
            print(f"Error loading bigrams: {e}")
            import traceback
            traceback.print_exc()

    def clean_word(self, word: str) -> str:
        """Remove punctuation and extra spaces from word"""
        # Remove punctuation and convert to lowercase
        cleaned = re.sub(r'[.,!?;:"\'\(\)\[\]]', '', word.lower())
        # Remove extra spaces
        cleaned = cleaned.strip()
        return cleaned

    def get_suggestions(self, text: str, n: int = 5) -> list:
        """Get word suggestions based on current text"""
        # Split text into words and clean each word
        words = [self.clean_word(w) for w in text.strip().split()]
        # Remove empty strings that might result from cleaning
        words = [w for w in words if w]
        
        if not words:
            return []
        
        # Check if the text ends with a space or punctuation
        ends_with_space = text.strip()[-1] if text.strip() else ''
        is_word_completed = ends_with_space in [' ', ',', '.', '!', '?', ';', ':']
        
        if is_word_completed:
            # If word is completed, suggest next words based on the last completed word
            if words:  # If we have at least one word
                return self.get_bigram_suggestions(words[-1], "", n)
            return []
        else:
            # If word is not completed, provide suggestions for current word
            last_word = words[-1]
            if len(words) == 1:
                return self.get_unigram_suggestions(last_word, n)
            else:
                prev_word = words[-2]
                return self.get_bigram_suggestions(prev_word, last_word, n)

    def get_unigram_suggestions(self, prefix: str, n: int = 5) -> list:
        # First check user memory
        user_suggestions = set()  # Use set to track suggestions
        if self.user_memory:
            words_freq = []
            self.user_memory.unigram_trie._collect_words_with_prefix(
                self.user_memory.unigram_trie.root, prefix, words_freq)
            # Add only frequent enough words
            for word, freq in words_freq:
                if freq >= self.user_memory.frequency_threshold:
                    user_suggestions.add(word)
        
        # Then get suggestions from main trie, excluding ones we already have
        main_suggestions = []
        if len(user_suggestions) < n:
            all_main = self.unigram_trie.get_top_n_prefixed(prefix, n)
            # Only add suggestions we haven't seen yet
            for word in all_main:
                if word not in user_suggestions and len(main_suggestions) < (n - len(user_suggestions)):
                    main_suggestions.append(word)
        
        # Combine suggestions, maintaining order (user memory first)
        return list(user_suggestions) + main_suggestions

    def get_bigram_suggestions(self, prev_word: str, current_prefix: str, n: int = 5) -> list:
        # First check user memory
        user_suggestions = set()  # Use set to track suggestions
        if self.user_memory and prev_word in self.user_memory.bigram_tries:
            words_freq = []
            self.user_memory.bigram_tries[prev_word]._collect_words_with_prefix(
                self.user_memory.bigram_tries[prev_word].root, current_prefix, words_freq)
            # Add only frequent enough words
            for word, freq in words_freq:
                if freq >= self.user_memory.frequency_threshold:
                    user_suggestions.add(word)
        
        # Then get suggestions from main tries, excluding ones we already have
        main_suggestions = []
        if len(user_suggestions) < n and prev_word in self.bigram_tries:
            all_main = self.bigram_tries[prev_word].get_top_n_prefixed(current_prefix, n)
            # Only add suggestions we haven't seen yet
            for word in all_main:
                if word not in user_suggestions and len(main_suggestions) < (n - len(user_suggestions)):
                    main_suggestions.append(word)
        
        # Combine suggestions, maintaining order (user memory first)
        return list(user_suggestions) + main_suggestions 