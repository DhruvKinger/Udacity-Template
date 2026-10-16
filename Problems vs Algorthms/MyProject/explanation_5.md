# Problem 5: Autocomplete with Tries

## Design choices
A trie is the natural data structure for autocomplete because words that share a prefix share the same path of nodes. Once I have walked down the path for a prefix, every word that starts with it lies in the subtree below that point, so I never have to compare the prefix against the whole word list. Each `TrieNode` stores its children in a dictionary keyed by character, which gives fast average O(1) child lookups and avoids allocating 26 slots per node, and an `is_word` flag marking where a complete word ends (needed because "ant" is a word and also a prefix of "anthology").

To collect the completions, `suffixes` does a depth-first search from the prefix node, building each suffix as it goes. I wrote it with an explicit stack rather than recursion so very long words cannot hit Python's recursion limit. The results are sorted at the end only so that the output is in a predictable order. If the prefix is not in the trie, `find` returns `None` and an empty list is returned.

## Efficiency
- **Insert: O(L)** time for a word of length `L`; space O(L) in the worst case, when none of the word is shared with existing words.
- **Find prefix: O(P)** time for a prefix of length `P`, one dictionary lookup per character.
- **Suffixes: O(P + K)** time to find the prefix and then visit the `K` nodes below it, plus O(m log m) for sorting the `m` results returned. Only the matching part of the trie is visited, not all stored words.
- **Space:** O(N) overall for the trie, where `N` is the total number of characters across the stored words (less when prefixes are shared).
