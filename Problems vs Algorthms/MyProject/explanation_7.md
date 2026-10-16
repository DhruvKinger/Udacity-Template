# Problem 7: HTTPRouter using a Trie

## Design choices
A trie fits routing well because many URLs share a beginning, such as `/blog/...` or `/home/about`. Rather than splitting paths into single letters, as in the autocomplete trie, I split on `/` so each node represents one path part. This keeps the trie small and shortens lookups, because the number of steps depends on how many parts a path has, not how many characters.

Each `RouteTrieNode` has a dictionary of children and a `handler`. The handler is stored only at the last node of a route, so `/home` returns the not-found handler even though `/home/about` exists: the intermediate node has no handler. `RouteTrie` handles `insert` and `find` on lists of parts, and `Router` is a thin wrapper that splits the path and adds the not-found fallback. All splitting lives in one `split_path` method used by both `add_handler` and `lookup`, so they always agree on how a path is read. It drops empty parts, which handles several edge cases at once: trailing slashes (`/about/` equals `/about`), repeated slashes, and `""` or `/` both mapping to the root handler.

## Efficiency
Let `c` be the number of characters in the path, `L` the number of parts after splitting, and `N` the total number of nodes stored in the trie.

**Time complexity: O(c) for `add_handler` and `lookup`.**
- *Path splitting:* `split_path` scans the `c` characters once with `str.split("/")`, then the list comprehension filters the `L` parts, so this step costs O(c).
- *Trie traversal:* `insert` and `find` do one dictionary lookup per part. A dictionary lookup is O(1) on average, so walking the trie costs O(L). Since `L <= c`, the traversal never costs more than the split.
- Neither step depends on how many routes are stored. A router with 10 routes and one with 10,000 routes take about the same time to look up the same path, which is the main advantage over checking a list of routes one by one (O(R) for R routes).

**Space complexity: O(N) for the router, O(c) extra per call.**
- *Stored nodes:* each distinct path part creates one `RouteTrieNode` with its own children dictionary, so the trie uses O(N) memory. Routes that start the same way, such as `/home/about` and `/home/contact`, share the `home` node, so `N` is usually smaller than the total number of parts across all routes.
- *Per call:* `split_path` builds a list of `L` parts, so each `add_handler` or `lookup` call uses O(c) temporary memory, which is freed afterwards. `lookup` itself keeps only one `node` variable while walking down the trie.
