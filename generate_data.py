# generate_data.py
import json
import re

chapters_meta = [
    {
        "id": 1,
        "name": "Foundations & Programming Basics",
        "phase": "Phase 0 · Foundations",
        "count": 13,
        "budget": "5.3 h",
        "patterns": [
            "Constraint to complexity: n<=10 -> O(n!); n<=20 -> O(2^n * n); n<=500 -> O(n^3); n<=5000 -> O(n^2); n<=1e5..2e5 -> O(n log n); n<=1e6..1e7 -> O(n); n<=1e18 -> O(log n) / O(1).",
            "Always test: empty input, single element, all equal, sorted, reverse sorted, maximum size, negative numbers, overflow.",
            "Solve on paper first. If you cannot explain your approach in 3 sentences, you do not have it yet."
        ]
    },
    {
        "id": 2,
        "name": "Arrays & Matrices",
        "phase": "Phase 1 · Core Data Structures",
        "count": 20,
        "budget": "10.6 h",
        "patterns": [
            "If array values lie in [1..n] -> try cyclic sort / negative-marking to detect duplicates & missing.",
            "If 'in-place with O(1) space' -> read pointer + write pointer, or reversal tricks.",
            "If 'subarray sum/product' -> Kadane or prefix technique. If 'subsequence' -> think DP/greedy.",
            "Matrix rotation = transpose + reverse rows. Spiral = maintain 4 boundaries."
        ]
    },
    {
        "id": 3,
        "name": "Strings",
        "phase": "Phase 1 · Core Data Structures",
        "count": 15,
        "budget": "7.2 h",
        "patterns": [
            "'Anagram / permutation' -> frequency array of 26 with a fixed-size window.",
            "'Longest substring with property' -> sliding window. 'Number of substrings' -> count contributions.",
            "'Compare/pair characters from both ends' -> two pointers. 'Palindrome' -> centre expansion.",
            "Building strings in a loop with + is O(n^2) in Java/Python; use join / StringBuilder / reserve."
        ]
    },
    {
        "id": 4,
        "name": "Hashing (HashMap / HashSet / Counting)",
        "phase": "Phase 1 · Core Data Structures",
        "count": 19,
        "budget": "10.0 h",
        "patterns": [
            "'Find pair/triple with property' -> complement in a set/map.",
            "'Count subarrays with sum K / divisible by K' -> prefix sums + hash map of prefix frequencies.",
            "'Group items that are equivalent' -> map from canonical key to list.",
            "'Longest sequence of consecutive integers' -> set + start-of-chain check."
        ]
    },
    {
        "id": 5,
        "name": "Sorting & Custom Comparators",
        "phase": "Phase 1 · Core Data Structures",
        "count": 15,
        "budget": "8.8 h",
        "patterns": [
            "'Sort then greedy scan' (meeting rooms, intervals, assignment).",
            "'Sort by one key, process with another structure' (heap / BIT / set) - the offline pattern.",
            "A comparator must be consistent: never return true for equal elements.",
            "If values are small integers (<= 1e6) consider counting sort / bucket sort."
        ]
    },
    {
        "id": 6,
        "name": "Binary Search (incl. Search on Answer)",
        "phase": "Phase 1 · Core Data Structures",
        "count": 17,
        "budget": "10.2 h",
        "patterns": [
            "Ask: 'Is there a monotone yes/no question over the answer space?' If yes -> binary search on answer.",
            "'Minimise the maximum' / 'maximise the minimum' / 'smallest x such that feasible' are the classic trigger phrases.",
            "Write the predicate first as a separate function; then the search loop is mechanical.",
            "For doubles: loop 100 iterations instead of while(hi-lo>eps)."
        ]
    },
    {
        "id": 7,
        "name": "Two Pointers & Sliding Window",
        "phase": "Phase 1 · Core Data Structures",
        "count": 21,
        "budget": "13.3 h",
        "patterns": [
            "Window validity must be monotone: growing the window can only make it 'more valid' (or the reverse).",
            "Longest window: shrink only when invalid. Shortest window: shrink while valid.",
            "Counting subarrays: for each right end, add (right - left + 1) valid starts.",
            "All positives + 'sum >= K' or 'sum <= K' -> window. Mixed signs -> prefix sums."
        ]
    },
    {
        "id": 8,
        "name": "Prefix Sums, Difference Arrays, Intervals & Sweep Line",
        "phase": "Phase 1 · Core Data Structures",
        "count": 20,
        "budget": "11.6 h",
        "patterns": [
            "'Many range updates, one final read' -> difference array.",
            "'Many range sum queries, no updates' -> prefix sums. With updates -> Fenwick/segment tree.",
            "'Overlapping intervals' -> sort by start (merge) or by end (max disjoint set).",
            "'Max simultaneous / minimum rooms' -> sweep events, or a min-heap of end times."
        ]
    },
    {
        "id": 9,
        "name": "Linked Lists",
        "phase": "Phase 1 · Core Data Structures",
        "count": 20,
        "budget": "11.0 h",
        "patterns": [
            "Always draw boxes and arrows. Track prev/curr/next explicitly.",
            "Use a dummy head when the head can change (delete, merge, partition).",
            "'Nth from end' -> two pointers n apart. 'Middle' -> slow/fast. 'Cycle' -> Floyd.",
            "Recursion on lists uses O(n) stack; prefer iteration when n is large."
        ]
    },
    {
        "id": 10,
        "name": "Stacks, Queues & Monotonic Structures",
        "phase": "Phase 1 · Core Data Structures",
        "count": 20,
        "budget": "12.6 h",
        "patterns": [
            "'Next greater/smaller to the left/right' -> monotonic stack, O(n).",
            "'Sum over all subarrays of min/max' -> find left/right span with monotonic stack, multiply.",
            "'Remove k digits/characters to get smallest/largest' -> greedy with monotonic stack.",
            "'Nested structure' (brackets, decode, tags) -> stack of partial results."
        ]
    },
    {
        "id": 11,
        "name": "Recursion & Backtracking",
        "phase": "Phase 2 · Core Algorithms",
        "count": 22,
        "budget": "14.7 h",
        "patterns": [
            "'Generate all ...' -> backtracking. 'Count ways' -> maybe DP; if state repeats, memoise.",
            "Duplicates in input: sort, then skip candidate if it equals the previous one at the same depth.",
            "Each level of recursion picks ONE thing (index or position); loops over choices at that level.",
            "If n <= 20 think bitmask; if n <= 40 think meet in the middle."
        ]
    },
    {
        "id": 12,
        "name": "Bit Manipulation",
        "phase": "Phase 2 · Core Algorithms",
        "count": 16,
        "budget": "8.0 h",
        "patterns": [
            "'Every element appears twice except one' -> XOR everything.",
            "'Subsets of a small set (n<=20)' -> bitmask loop. 'Assignments over n items' -> bitmask DP.",
            "'Maximise XOR' -> binary trie (greedy from high bit) or XOR basis.",
            "'Range AND' -> common prefix of the endpoints."
        ]
    },
    {
        "id": 13,
        "name": "Math, Number Theory & Combinatorics",
        "phase": "Phase 2 · Core Algorithms",
        "count": 22,
        "budget": "13.2 h",
        "patterns": [
            "'Answer modulo 1e9+7' -> keep everything modded; division = multiply by modular inverse.",
            "'n up to 1e18' -> matrix exponentiation / closed form / cycle detection.",
            "'Count pairs with gcd = 1' -> Mobius / inclusion-exclusion. 'Sum over divisors' -> sieve harmonic loops O(n log n).",
            "'Expected number of ...' -> linearity of expectation; do not enumerate outcomes."
        ]
    },
    {
        "id": 14,
        "name": "Greedy Algorithms",
        "phase": "Phase 2 · Core Algorithms",
        "count": 21,
        "budget": "12.9 h",
        "patterns": [
            "Try to sort by some key; if adjacent swap never hurts, that key is right (exchange argument).",
            "'Regret' greedy: take now, but keep a heap so you can undo the worst choice later.",
            "'Minimum number of X to cover' -> sort + sweep + always extend as far as possible.",
            "Prove or find a counter-example in 5 minutes; if none, code it. Otherwise fall back to DP."
        ]
    },
    {
        "id": 15,
        "name": "Heaps & Priority Queues",
        "phase": "Phase 2 · Core Algorithms",
        "count": 14,
        "budget": "9.3 h",
        "patterns": [
            "'K largest / smallest / most frequent' -> heap of size K. 'Merge K sorted things' -> heap of heads.",
            "'Median of a stream' -> max-heap for lower half + min-heap for upper half, rebalance.",
            "'Repeatedly take best available now, new items become available later' -> two heaps (availability + value).",
            "Dijkstra / Prim use a min-heap; with lazy deletion you push duplicates and skip stale entries."
        ]
    },
    {
        "id": 16,
        "name": "Binary Trees",
        "phase": "Phase 2 · Core Algorithms",
        "count": 30,
        "budget": "16.7 h",
        "patterns": [
            "Postorder ('bottom-up') for anything depending on children: height, diameter, balanced, max path sum.",
            "Preorder ('top-down') for anything depending on path from root: path sum, good nodes, root-to-leaf.",
            "BFS with a queue when the answer depends on levels; track level size.",
            "When answer can span through a node: compute best downward path per child and combine at node."
        ]
    },
    {
        "id": 17,
        "name": "BST, Balanced Trees & Ordered Sets",
        "phase": "Phase 2 · Core Algorithms",
        "count": 15,
        "budget": "8.4 h",
        "patterns": [
            "'Floor/ceiling/nearest key with insertions' -> ordered set.",
            "'Validate BST' -> pass (min,max) bounds or use in-order strictly increasing.",
            "'k-th smallest with updates' -> size-augmented BST / BIT over compressed values / treap.",
            "'Sliding window + order statistics' -> multiset with erase-one-occurrence."
        ]
    },
    {
        "id": 18,
        "name": "Tries (Prefix Trees)",
        "phase": "Phase 2 · Core Algorithms",
        "count": 10,
        "budget": "7.5 h",
        "patterns": [
            "'Prefix' in statement -> trie. 'Maximum XOR' -> binary trie.",
            "Store count/word-id at nodes for 'how many words start with p' or 'which words'.",
            "Search many words on a grid: build trie from words, DFS grid once, prune found branches."
        ]
    },
    {
        "id": 19,
        "name": "Graphs I: Traversal, Grids & Connectivity",
        "phase": "Phase 3 · Graph Algorithms",
        "count": 29,
        "budget": "16.8 h",
        "patterns": [
            "'Shortest number of steps, unit cost' -> BFS. 'Any path / component / reachability' -> DFS or BFS.",
            "'Simultaneous spreading' (rotting oranges, fire) -> multi-source BFS from all sources at once.",
            "'Minimum moves to transform state' -> BFS on the state graph; encode state compactly.",
            "'Is it two-colourable / odd cycle?' -> BFS/DFS colouring."
        ]
    },
    {
        "id": 20,
        "name": "Graphs II: Topological Sort, DSU, Shortest Paths & MST",
        "phase": "Phase 3 · Graph Algorithms",
        "count": 30,
        "budget": "18.8 h",
        "patterns": [
            "'Order tasks with prerequisites' -> topo sort. 'Cannot finish' -> cycle.",
            "'Are X and Y connected after unions' -> DSU. 'Group things' -> DSU.",
            "'Minimum cost path' -> Dijkstra; when state includes extra dimensions add them to node key.",
            "'Connect everything with minimum total cost' -> MST."
        ]
    },
    {
        "id": 21,
        "name": "Graphs III: Advanced (SCC, Bridges, Euler, Flows, Matching)",
        "phase": "Phase 4 · Advanced",
        "count": 18,
        "budget": "15.9 h",
        "patterns": [
            "'Mutual reachability' -> SCC. 'Critical connection' -> bridge. 'Robots must not disconnect' -> articulation points.",
            "'Pair up / assign each X to distinct Y' -> bipartite matching or flow. 'Minimum cut' -> max flow.",
            "'Boolean variables with pairwise constraints' -> 2-SAT.",
            "'Traverse every edge exactly once' -> Euler path."
        ]
    },
    {
        "id": 22,
        "name": "Trees II: LCA, Binary Lifting, Euler Tour, HLD, Centroid, Rerooting",
        "phase": "Phase 4 · Advanced",
        "count": 23,
        "budget": "17.9 h",
        "patterns": [
            "'Subtree query' -> Euler tour range. 'Path query' -> LCA + prefix or HLD.",
            "'For each node as root' -> rerooting DP with prefix/suffix aggregates.",
            "'Count/find paths of length K / with property' -> centroid decomposition.",
            "'Merge child structures, keep largest' -> small-to-large."
        ]
    },
    {
        "id": 23,
        "name": "Dynamic Programming I: Foundations",
        "phase": "Phase 3 · Dynamic Programming",
        "count": 33,
        "budget": "18.1 h",
        "patterns": [
            "Write recurrence in words first: 'dp[i][j] = best answer using first i items with capacity j'.",
            "'Number of ways' -> add; 'min/max' -> min/max; 'is it possible' -> boolean/bitset.",
            "Order of loops matters: combinations (items outer) vs permutations (target outer).",
            "If dp[i] depends only on dp[i-1], dp[i-2]... keep variables, not an array."
        ]
    },
    {
        "id": 24,
        "name": "Dynamic Programming II: Intermediate (Stocks, Intervals, Bitmask, Digit, Trees, Probability)",
        "phase": "Phase 3 · Dynamic Programming",
        "count": 35,
        "budget": "27.1 h",
        "patterns": [
            "Interval DP: iterate by length, choose the LAST operation to split the interval.",
            "Bitmask DP state: dp[mask][last]; transitions add one element; complexity O(2^n * n^2).",
            "Digit DP: always carry a 'tight' flag; memoise only when not tight.",
            "State machine: draw states as circles, transitions as arrows, then write dp per state."
        ]
    },
    {
        "id": 25,
        "name": "Dynamic Programming III: Advanced Optimisation",
        "phase": "Phase 4 · Advanced",
        "count": 12,
        "budget": "11.2 h",
        "patterns": [
            "cost(j,i) contains product a_j * b_i -> CHT. Sum of squares partition -> CHT / D&C.",
            "Partition into K groups with Monge cost -> D&C optimisation O(K n log n) or Knuth O(n^2).",
            "'Exactly K' with convex/concave answer in K -> aliens trick (binary search on lambda).",
            "Window/range max in transitions -> monotone deque; arbitrary range -> segment tree."
        ]
    },
    {
        "id": 26,
        "name": "Range Queries & Advanced Data Structures",
        "phase": "Phase 4 · Advanced",
        "count": 23,
        "budget": "19.8 h",
        "patterns": [
            "'Point updates + range sum' -> BIT. 'Range updates + range queries' -> segment tree with lazy.",
            "'Static array, many min/max queries' -> sparse table. 'Distinct in range / offline' -> BIT + last occurrence, or Mo.",
            "'k-th smallest in range / version history' -> persistent segment tree / wavelet tree.",
            "'Insert/delete/reverse a segment, index by position' -> implicit treap."
        ]
    },
    {
        "id": 27,
        "name": "Advanced Strings",
        "phase": "Phase 4 · Advanced",
        "count": 15,
        "budget": "12.2 h",
        "patterns": [
            "'Find pattern(s) in text' -> KMP/Z (one), Aho-Corasick (many), hashing (many, probabilistic).",
            "'Number of distinct substrings / k-th substring / LCP queries' -> suffix array or automaton.",
            "'Palindromic substrings' -> Manacher / hashing / eertree. 'Periodic / border' -> prefix function.",
            "'Count strings of length n avoiding patterns' -> Aho-Corasick + DP."
        ]
    },
    {
        "id": 28,
        "name": "Computational Geometry",
        "phase": "Phase 4 · Advanced",
        "count": 15,
        "budget": "10.3 h",
        "patterns": [
            "Always prefer integer cross products; compare with 0, never with doubles when input is integral.",
            "Convex hull + rotating calipers for 'farthest pair / minimum bounding box' queries.",
            "Manhattan distance -> transform (x+y, x-y) and use Chebyshev distance."
        ]
    },
    {
        "id": 29,
        "name": "Game Theory",
        "phase": "Phase 4 · Advanced",
        "count": 11,
        "budget": "6.5 h",
        "patterns": [
            "Compute win/lose for small n by brute force, write table, look for pattern (period / mod k / XOR).",
            "Independent sub-games -> XOR of Grundy values. Single pile with move sets -> mex over reachable Grundy values.",
            "Optimal-play array games -> dp[l][r] = best score difference for current player."
        ]
    },
    {
        "id": 30,
        "name": "Design & Implementation Problems",
        "phase": "Phase 3 · Applied",
        "count": 15,
        "budget": "10.8 h",
        "patterns": [
            "O(1) get/put with eviction order -> hash map + linked list.",
            "O(1) getRandom -> array + hash map of value->index with swap-delete.",
            "'Top K at any time / trending' -> heap + lazy deletion or ordered set.",
            "Read required complexity carefully; it dictates data structure."
        ]
    },
    {
        "id": 31,
        "name": "Simulation, Constructive, Ad-hoc & Interactive",
        "phase": "Phase 4 · Contest Skills",
        "count": 19,
        "budget": "10.2 h",
        "patterns": [
            "Small cases first: brute-force n=1..8, print outputs, look for pattern, then prove.",
            "Constructive: try greedy building from largest/smallest, pair elements, or use parity classes.",
            "Interactive: binary search on answer with at most ceil(log2 n) queries; always flush."
        ]
    },
    {
        "id": 32,
        "name": "Mixed Contest Sets & Advanced Math",
        "phase": "Phase 4 · Contest Skills",
        "count": 2,
        "budget": "0.9 h",
        "patterns": [
            "Keep an 'error log': problem, why you failed (idea / proof / bug / speed), what to practise.",
            "Re-solve every failed problem after 1 day, 1 week and 1 month (spaced repetition)."
        ]
    }
]

def slugify(title):
    clean = re.sub(r'\[.*?\]', '', title)
    clean = clean.replace('$', '').strip()
    clean = clean.replace("`", "")
    clean = clean.replace("'", "")
    clean = clean.replace('"', '')
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', clean)
    clean = re.sub(r'[\s_]+', '-', clean).lower()
    return clean.strip('-')

def get_url(title):
    if title.startswith("[CSES]"):
        name = title.replace("[CSES]", "").strip()
        slug = slugify(name)
        return f"https://cses.fi/problemset/task/{slug}"
    elif title.startswith("[AtCoder]"):
        # e.g. [AtCoder] Educational DP A - Frog 1 -> https://atcoder.jp/contests/dp/tasks/dp_a
        m = re.search(r'Educational DP ([A-Z])', title)
        if m:
            code = m.group(1).lower()
            return f"https://atcoder.jp/contests/dp/tasks/dp_{code}"
        return "https://atcoder.jp/contests/dp/tasks"
    elif title.startswith("[LibChk]"):
        if "10^9+7" in title:
            return "https://judge.yosupo.jp/problem/convolution_mod_1000000007"
        return "https://judge.yosupo.jp/problem/convolution_mod"
    else:
        slug = slugify(title)
        return f"https://leetcode.com/problems/{slug}/"

# All raw problem rows (id, raw_title, level, list_tag, hint, chapter_id)
raw_problems = [
    # Ch 1 (1-13)
    (1, "Fizz Buzz", "E", "", "loops + conditions", 1),
    (2, "Palindrome Number", "E", "TI150", "digit extraction with % and /", 1),
    (3, "Reverse Integer", "M", "NC150", "overflow checking", 1),
    (4, "Roman to Integer", "E", "TI150", "mapping + scan with lookahead", 1),
    (5, "Integer to Roman", "M", "TI150", "greedy over a value table", 1),
    (6, "Plus One", "E", "NC150", "carry propagation", 1),
    (7, "Count Primes", "M", "", "sieve of Eratosthenes", 1),
    (8, "Pow(x, n)", "M", "NC150", "fast exponentiation, recursion halving", 1),
    (9, "Happy Number", "E", "NC150", "cycle detection with a set", 1),
    (10, "Sqrt(x)", "E", "TI150", "integer binary search", 1),
    (11, "[CSES] Weird Algorithm", "E", "", "I/O, loops, 64-bit ints. Simulate: even -> n/2, odd -> 3n+1.", 1),
    (12, "[CSES] Missing Number", "E", "", "sum/XOR trick for the missing element: n(n+1)/2 - sum, or XOR all.", 1),
    (13, "[CSES] Repetitions", "E", "", "run-length scanning: track current run of equal letters and best run.", 1),

    # Ch 2 (14-33)
    (14, "Maximum Subarray", "M", "B75", "Kadane's algorithm", 2),
    (15, "Best Time to Buy and Sell Stock", "E", "B75", "running minimum", 2),
    (16, "Product of Array Except Self", "M", "B75", "prefix x suffix without division", 2),
    (17, "Move Zeroes", "E", "", "read/write pointers, in place", 2),
    (18, "Rotate Array", "M", "TI150", "rotation by three reversals", 2),
    (19, "Sort Colors", "M", "", "Dutch national flag 3-way partition", 2),
    (20, "Next Permutation", "M", "", "permutation successor algorithm", 2),
    (21, "First Missing Positive", "H", "", "array as its own hash (cyclic placement)", 2),
    (22, "Find All Duplicates in an Array", "M", "", "negative marking trick", 2),
    (23, "Majority Element", "E", "TI150", "Boyer-Moore voting", 2),
    (24, "Merge Sorted Array", "E", "TI150", "fill from the back", 2),
    (25, "Remove Element", "E", "TI150", "overwrite pointer", 2),
    (26, "Remove Duplicates from Sorted Array", "E", "TI150", "write index on sorted data", 2),
    (27, "Remove Duplicates from Sorted Array II", "M", "TI150", "keep at most two copies", 2),
    (28, "Maximum Product Subarray", "M", "B75", "track both max and min", 2),
    (29, "Maximum Sum Circular Subarray", "M", "TI150", "wrap-around via total minus min", 2),
    (30, "Spiral Matrix", "M", "B75", "four moving boundaries", 2),
    (31, "Rotate Image", "M", "B75", "transpose + reverse", 2),
    (32, "Set Matrix Zeroes", "M", "B75", "O(1) space using first row/col as flags", 2),
    (33, "Search a 2D Matrix II", "M", "", "staircase search from a corner", 2),

    # Ch 3 (34-48)
    (34, "Valid Anagram", "E", "B75", "frequency array of 26", 3),
    (35, "Longest Common Prefix", "E", "TI150", "vertical scan", 3),
    (36, "Valid Palindrome", "E", "B75", "two pointers + filtering", 3),
    (37, "Longest Palindromic Substring", "M", "B75", "expand around centre", 3),
    (38, "Palindromic Substrings", "M", "B75", "counting via centre expansion", 3),
    (39, "Reverse Words in a String", "M", "TI150", "tokenising and rebuilding", 3),
    (40, "Length of Last Word", "E", "TI150", "scan from the end", 3),
    (41, "String to Integer (atoi)", "M", "", "careful parsing state machine", 3),
    (42, "Multiply Strings", "M", "NC150", "grade-school big-number multiply", 3),
    (43, "Find All Anagrams in a String", "M", "", "fixed window frequency compare", 3),
    (44, "Find the Index of the First Occurrence in a String", "E", "TI150", "pattern matching (naive then KMP)", 3),
    (45, "Repeated Substring Pattern", "E", "", "(s+s) trick / prefix function", 3),
    (46, "Zigzag Conversion", "M", "TI150", "index simulation by rows", 3),
    (47, "Group Shifted Strings $", "M", "", "canonical form for equivalence", 3),
    (48, "Encode and Decode Strings $", "M", "B75", "length-prefix serialisation", 3),

    # Ch 4 (49-67)
    (49, "Two Sum", "E", "B75", "complement lookup in a map", 4),
    (50, "Contains Duplicate", "E", "B75", "set membership", 4),
    (51, "Group Anagrams", "M", "B75", "canonical key grouping", 4),
    (52, "Top K Frequent Elements", "M", "B75", "frequency map + bucket/heap", 4),
    (53, "Longest Consecutive Sequence", "M", "B75", "set + start-of-chain check", 4),
    (54, "Subarray Sum Equals K", "M", "", "prefix sums + hash map", 4),
    (55, "Continuous Subarray Sum", "M", "", "prefix mod K with first index", 4),
    (56, "Contiguous Array", "M", "", "map +1/-1 running balance", 4),
    (57, "4Sum II", "M", "", "meet in the middle with a map", 4),
    (58, "Insert Delete GetRandom O(1)", "M", "TI150", "array + map with swap-delete", 4),
    (59, "LRU Cache", "M", "NC150", "hash map + doubly linked list", 4),
    (60, "Valid Sudoku", "M", "NC150", "hashing rows/cols/boxes", 4),
    (61, "Time Based Key-Value Store", "M", "NC150", "map to sorted versions + binary search", 4),
    (62, "Brick Wall", "M", "", "count aligned edges with a map", 4),
    (63, "Max Points on a Line", "H", "TI150", "hash by normalised slope", 4),
    (64, "Isomorphic Strings", "E", "TI150", "bijection check with two maps", 4),
    (65, "Ransom Note", "E", "TI150", "frequency counting", 4),
    (66, "Word Pattern", "E", "TI150", "bijection between pattern and words", 4),
    (67, "Contains Duplicate II", "E", "TI150", "map of last seen index", 4),

    # Ch 5 (68-82)
    (68, "Sort an Array", "M", "", "implement merge sort", 5),
    (69, "Largest Number", "M", "", "custom comparator (a+b vs b+a)", 5),
    (70, "Kth Largest Element in an Array", "M", "NC150", "quickselect", 5),
    (71, "Queue Reconstruction by Height", "M", "", "sort by two keys then insert", 5),
    (72, "Count of Smaller Numbers After Self", "H", "", "merge-sort counting", 5),
    (73, "Reverse Pairs", "H", "", "modified merge sort", 5),
    (74, "H-Index", "M", "TI150", "sort + scan / counting sort", 5),
    (75, "Sort Characters By Frequency", "M", "", "sort by frequency key", 5),
    (76, "Custom Sort String", "M", "", "order defined by another string", 5),
    (77, "Relative Sort Array", "E", "", "counting sort with a given order", 5),
    (78, "Wiggle Sort II", "M", "", "sort then interleave halves", 5),
    (79, "Maximum Gap", "M", "", "bucket / radix idea", 5),
    (80, "[CSES] Distinct Numbers", "E", "", "sort/set for distinct values", 5),
    (81, "[CSES] Apartments", "E", "", "sort + two pointers matching applicant to apartment", 5),
    (82, "[CSES] Concert Tickets", "M", "", "multiset lower_bound for price matching", 5),

    # Ch 6 (83-99)
    (83, "Binary Search", "E", "NC150", "the basic loop and invariants", 6),
    (84, "Search Insert Position", "E", "TI150", "lower bound", 6),
    (85, "Find First and Last Position of Element in Sorted Array", "M", "TI150", "left/right bound", 6),
    (86, "Search in Rotated Sorted Array", "M", "B75", "decide which half is sorted", 6),
    (87, "Find Minimum in Rotated Sorted Array", "M", "B75", "binary search on a pivot", 6),
    (88, "Find Peak Element", "M", "TI150", "binary search without a sorted array", 6),
    (89, "Search a 2D Matrix", "M", "NC150", "flatten to 1D indices", 6),
    (90, "Single Element in a Sorted Array", "M", "", "binary search on parity", 6),
    (91, "Find K Closest Elements", "M", "", "binary search on window start", 6),
    (92, "Koko Eating Bananas", "M", "NC150", "search on the answer", 6),
    (93, "Capacity To Ship Packages Within D Days", "M", "", "feasibility check function", 6),
    (94, "Split Array Largest Sum", "H", "", "minimise the maximum", 6),
    (95, "Minimum Number of Days to Make m Bouquets", "M", "", "monotone predicate", 6),
    (96, "Magnetic Force Between Two Balls", "M", "", "maximise the minimum", 6),
    (97, "Kth Smallest Element in a Sorted Matrix", "M", "", "binary search on value range", 6),
    (98, "Median of Two Sorted Arrays", "H", "NC150", "partition binary search", 6),
    (99, "[CSES] Factory Machines", "M", "", "answer search with a time predicate", 6),

    # Ch 7 (100-120)
    (100, "Two Sum II - Input Array Is Sorted", "M", "NC150", "opposite-end pointers", 7),
    (101, "3Sum", "M", "B75", "sort + fix one + two pointers, skip duplicates", 7),
    (102, "Container With Most Water", "M", "B75", "move the shorter side", 7),
    (103, "Trapping Rain Water", "H", "NC150", "two-pointer running maxima", 7),
    (104, "Boats to Save People", "M", "", "greedy pairing with two pointers", 7),
    (105, "Valid Triangle Number", "M", "", "sort + two pointers counting", 7),
    (106, "Is Subsequence", "E", "TI150", "greedy two pointers", 7),
    (107, "Maximum Average Subarray I", "E", "", "fixed-size window", 7),
    (108, "Longest Substring Without Repeating Characters", "M", "B75", "variable window + last-seen map", 7),
    (109, "Longest Repeating Character Replacement", "M", "B75", "window with max-frequency trick", 7),
    (110, "Permutation in String", "M", "NC150", "window frequency comparison", 7),
    (111, "Substring with Concatenation of All Words", "H", "TI150", "window stepping by word length", 7),
    (112, "Minimum Window Substring", "H", "B75", "shrink while valid", 7),
    (113, "Minimum Size Subarray Sum", "M", "TI150", "shortest window, positives only", 7),
    (114, "Fruit Into Baskets", "M", "", "at most K distinct", 7),
    (115, "Max Consecutive Ones III", "M", "", "window with flip budget", 7),
    (116, "Subarrays with K Different Integers", "H", "", "exactly K = atMost(K) - atMost(K-1)", 7),
    (117, "Sliding Window Maximum", "H", "NC150", "monotonic deque", 7),
    (118, "Get Equal Substrings Within Budget", "M", "", "window on cost array", 7),
    (119, "[CSES] Playlist", "E", "", "sliding window with a set/map", 7),
    (120, "[CSES] Subarray Sums I", "E", "", "sliding sum with target, two pointers", 7),

    # Ch 8 (121-140)
    (121, "Range Sum Query - Immutable", "E", "", "1D prefix sums", 8),
    (122, "Range Sum Query 2D - Immutable", "M", "", "2D prefix sums", 8),
    (123, "Find Pivot Index", "E", "", "prefix vs suffix balance", 8),
    (124, "Corporate Flight Bookings", "M", "", "difference array", 8),
    (125, "Car Pooling", "M", "", "difference array / sweep", 8),
    (126, "Range Addition $", "M", "", "apply updates then prefix", 8),
    (127, "Merge Intervals", "M", "B75", "sort by start + merge", 8),
    (128, "Insert Interval", "M", "B75", "linear merge insertion", 8),
    (129, "Interval List Intersections", "M", "", "two-pointer over intervals", 8),
    (130, "Meeting Rooms $", "E", "B75", "sort and check overlap", 8),
    (131, "Meeting Rooms II $", "M", "B75", "sweep / min-heap of end times", 8),
    (132, "Employee Free Time $", "H", "", "merge all busy intervals", 8),
    (133, "Summary Ranges", "E", "TI150", "group consecutive runs", 8),
    (134, "Minimum Interval to Include Each Query", "H", "NC150", "offline sort + heap", 8),
    (135, "The Skyline Problem", "H", "", "sweep line with heap", 8),
    (136, "Number of Submatrices That Sum to Target", "H", "", "2D prefix + hash map", 8),
    (137, "Maximum Population Year", "E", "", "events / difference array", 8),
    (138, "[CSES] Static Range Sum Queries", "E", "", "static range sum via prefix array", 8),
    (139, "[CSES] Forest Queries", "E", "", "2D prefix sums with inclusion-exclusion", 8),
    (140, "[CSES] Restaurant Customers", "M", "", "sweep line over arrivals/departures", 8),

    # Ch 9 (141-160)
    (141, "Reverse Linked List", "E", "B75", "iterative pointer reversal", 9),
    (142, "Merge Two Sorted Lists", "E", "B75", "dummy head merge", 9),
    (143, "Linked List Cycle", "E", "B75", "Floyd fast/slow pointers", 9),
    (144, "Linked List Cycle II", "M", "", "locate the cycle entry", 9),
    (145, "Middle of the Linked List", "E", "", "slow/fast midpoint", 9),
    (146, "Remove Nth Node From End of List", "M", "B75", "two pointers n apart", 9),
    (147, "Reorder List", "M", "B75", "middle + reverse + interleave", 9),
    (148, "Palindrome Linked List", "E", "", "reverse second half", 9),
    (149, "Add Two Numbers", "M", "NC150", "carry across lists", 9),
    (150, "Intersection of Two Linked Lists", "E", "", "length equalising pointer swap", 9),
    (151, "Copy List with Random Pointer", "M", "NC150", "interleave or map for deep copy", 9),
    (152, "Sort List", "M", "TI150", "merge sort on a list", 9),
    (153, "Reverse Linked List II", "M", "TI150", "reverse a sub-range", 9),
    (154, "Reverse Nodes in k-Group", "H", "NC150", "k-group reversal", 9),
    (155, "Merge k Sorted Lists", "H", "B75", "heap or divide and conquer", 9),
    (156, "Odd Even Linked List", "M", "", "splitting into two lists", 9),
    (157, "Remove Duplicates from Sorted List II", "M", "TI150", "dummy head + skip runs", 9),
    (158, "Find the Duplicate Number", "M", "NC150", "Floyd on an implicit list", 9),
    (159, "Partition List", "M", "TI150", "two dummy lists", 9),
    (160, "Rotate List", "M", "TI150", "make circular, cut at n-k", 9),

    # Ch 10 (161-180)
    (161, "Valid Parentheses", "E", "B75", "stack matching", 10),
    (162, "Min Stack", "M", "NC150", "auxiliary min tracking", 10),
    (163, "Evaluate Reverse Polish Notation", "M", "NC150", "stack evaluation", 10),
    (164, "Daily Temperatures", "M", "NC150", "monotonic stack, next greater", 10),
    (165, "Next Greater Element II", "M", "", "circular monotonic stack", 10),
    (166, "Online Stock Span", "M", "", "monotonic stack with counts", 10),
    (167, "Largest Rectangle in Histogram", "H", "NC150", "monotonic stack spans", 10),
    (168, "Maximal Rectangle", "H", "", "histogram per row", 10),
    (169, "Car Fleet", "M", "NC150", "sort + stack of arrival times", 10),
    (170, "Remove K Digits", "M", "", "greedy monotonic stack", 10),
    (171, "Decode String", "M", "", "stack of partial results", 10),
    (172, "Basic Calculator II", "M", "", "operator precedence with a stack", 10),
    (173, "Basic Calculator", "H", "TI150", "parentheses and sign stack", 10),
    (174, "Asteroid Collision", "M", "", "stack simulation", 10),
    (175, "Simplify Path", "M", "TI150", "stack of path parts", 10),
    (176, "Sum of Subarray Minimums", "M", "", "contribution technique", 10),
    (177, "Implement Queue using Stacks", "E", "", "amortised two-stack queue", 10),
    (178, "Shortest Subarray with Sum at Least K", "H", "", "monotonic deque on prefix sums", 10),
    (179, "[CSES] Nearest Smaller Values", "E", "", "monotonic stack of indices", 10),
    (180, "[CSES] Sliding Window Minimum", "M", "", "monotonic deque of window indices", 10),

    # Ch 11 (181-202)
    (181, "Subsets", "M", "NC150", "include/exclude recursion", 11),
    (182, "Subsets II", "M", "NC150", "skip duplicates at the same depth", 11),
    (183, "Permutations", "M", "NC150", "used[] backtracking", 11),
    (184, "Permutations II", "M", "", "duplicate handling with sorting", 11),
    (185, "Combinations", "M", "TI150", "choose k with start index", 11),
    (186, "Combination Sum", "M", "NC150", "unbounded reuse with start index", 11),
    (187, "Combination Sum II", "M", "NC150", "each element once, skip duplicates", 11),
    (188, "Letter Combinations of a Phone Number", "M", "NC150", "product of choices", 11),
    (189, "Generate Parentheses", "M", "NC150", "open/close counters", 11),
    (190, "Palindrome Partitioning", "M", "NC150", "partition + palindrome check", 11),
    (191, "Word Search", "M", "B75", "grid DFS with visited undo", 11),
    (192, "N-Queens", "H", "NC150", "column/diagonal sets", 11),
    (193, "Restore IP Addresses", "M", "", "segment-count pruning", 11),
    (194, "Matchsticks to Square", "M", "", "pruning with sorted sides", 11),
    (195, "Partition to K Equal Sum Subsets", "M", "", "bitmask/memo vs backtracking", 11),
    (196, "Expression Add Operators", "H", "", "evaluate while building", 11),
    (197, "Sudoku Solver", "H", "", "constraint propagation search", 11),
    (198, "N-Queens II", "H", "TI150", "count placements with bitmasks", 11),
    (199, "Construct Quad Tree", "M", "TI150", "divide and conquer on a grid", 11),
    (200, "[CSES] Apple Division", "E", "", "subset enumeration: bitmask minimise difference", 11),
    (201, "[CSES] Chessboard and Queens", "M", "", "placement backtracking row by row", 11),
    (202, "[CSES] Meet in the Middle", "H", "", "split array in halves, sorted subset sums", 11),

    # Ch 12 (203-218)
    (203, "Single Number", "E", "NC150", "XOR cancellation", 12),
    (204, "Single Number II", "M", "TI150", "count bits mod 3", 12),
    (205, "Single Number III", "M", "", "split by a set bit", 12),
    (206, "Number of 1 Bits", "E", "B75", "Kernighan's n & (n-1)", 12),
    (207, "Add Binary", "E", "TI150", "bitwise addition with carry", 12),
    (208, "Counting Bits", "E", "B75", "dp[i] = dp[i>>1] + (i&1)", 12),
    (209, "Reverse Bits", "E", "B75", "shifting and masking", 12),
    (210, "Missing Number", "E", "B75", "XOR with indices", 12),
    (211, "Power of Two", "E", "", "single set bit test", 12),
    (212, "Sum of Two Integers", "M", "B75", "add with XOR and carry", 12),
    (213, "Bitwise AND of Numbers Range", "M", "TI150", "common prefix of endpoints", 12),
    (214, "Maximum XOR of Two Numbers in an Array", "M", "", "binary trie / prefix set", 12),
    (215, "Divide Two Integers", "M", "", "shift-subtract division", 12),
    (216, "Maximum Product of Word Lengths", "M", "", "bitmask per word", 12),
    (217, "Minimum Flips to Make a OR b Equal to c", "M", "", "per-bit case analysis", 12),
    (218, "[CSES] Maximum Xor Subarray", "H", "", "binary trie for max XOR subarray", 12),

    # Ch 13 (219-240)
    (219, "Factorial Trailing Zeroes", "M", "TI150", "count factors of 5", 13),
    (220, "Greatest Common Divisor of Strings", "E", "", "Euclid on lengths", 13),
    (221, "Ugly Number II", "M", "", "multiple pointers / heap", 13),
    (222, "Perfect Squares", "M", "", "Lagrange/DP, math insight", 13),
    (223, "Super Pow", "M", "", "modular exponent by digits", 13),
    (224, "Water and Jug Problem", "M", "", "Bezout's identity", 13),
    (225, "Unique Paths", "M", "B75", "binomial coefficient counting", 13),
    (226, "Fraction to Recurring Decimal", "M", "", "long division with remainder map", 13),
    (227, "Random Pick with Weight", "M", "", "prefix sums + binary search", 13),
    (228, "Shuffle an Array", "M", "", "Fisher-Yates shuffle", 13),
    (229, "Linked List Random Node", "M", "", "reservoir sampling", 13),
    (230, "Count Good Numbers", "M", "", "modular fast power", 13),
    (231, "Nth Digit", "M", "", "digit-length bucketing", 13),
    (232, "Number of Music Playlists", "H", "", "combinatorial DP", 13),
    (233, "[CSES] Exponentiation", "E", "", "binary exponentiation mod p", 13),
    (234, "[CSES] Exponentiation II", "M", "", "Fermat/Euler exponent reduction", 13),
    (235, "[CSES] Sum of Divisors", "M", "", "sum of divisors by blocks", 13),
    (236, "[CSES] Binomial Coefficients", "M", "", "nCr with factorial tables", 13),
    (237, "[CSES] Counting Divisors", "M", "", "divisor counting via sieve/factorisation", 13),
    (238, "[CSES] Fibonacci Numbers", "M", "", "matrix exponentiation, n up to 1e18", 13),
    (239, "[CSES] Christmas Party", "M", "", "derangements recurrence", 13),
    (240, "[CSES] Counting Coprime Pairs", "H", "", "Mobius / inclusion-exclusion counting", 13),

    # Ch 14 (241-261)
    (241, "Jump Game", "M", "B75", "greedy farthest reach", 14),
    (242, "Jump Game II", "M", "NC150", "greedy BFS layers", 14),
    (243, "Gas Station", "M", "NC150", "running surplus reset", 14),
    (244, "Best Time to Buy and Sell Stock II", "M", "TI150", "sum of positive gaps", 14),
    (245, "Candy", "H", "TI150", "two-pass constraint satisfaction", 14),
    (246, "Assign Cookies", "E", "", "sort + match", 14),
    (247, "Partition Labels", "M", "NC150", "last occurrence intervals", 14),
    (248, "Non-overlapping Intervals", "M", "B75", "earliest end first", 14),
    (249, "Minimum Number of Arrows to Burst Balloons", "M", "TI150", "interval piercing", 14),
    (250, "Hand of Straights", "M", "NC150", "greedy grouping with a map", 14),
    (251, "Valid Parenthesis String", "M", "NC150", "range of open counts", 14),
    (252, "Merge Triplets to Form Target Triplet", "M", "NC150", "greedy filtering of usable triplets", 14),
    (253, "Task Scheduler", "M", "NC150", "max frequency formula", 14),
    (254, "Two City Scheduling", "M", "", "sort by cost difference", 14),
    (255, "Reorganize String", "M", "", "heap by frequency", 14),
    (256, "Maximum Units on a Truck", "E", "", "sort by value", 14),
    (257, "IPO", "H", "TI150", "regret greedy with two heaps", 14),
    (258, "Course Schedule III", "H", "", "deadline greedy with a max-heap", 14),
    (259, "Minimum Number of Refueling Stops", "H", "", "take the best fuel retroactively", 14),
    (260, "[CSES] Tasks and Deadlines", "E", "", "exchange argument: sort by duration", 14),
    (261, "[CSES] Reading Books", "E", "", "prove a lower bound, then achieve it", 14),

    # Ch 15 (262-275)
    (262, "Kth Largest Element in a Stream", "E", "NC150", "size-K min-heap", 15),
    (263, "Last Stone Weight", "E", "NC150", "max-heap simulation", 15),
    (264, "K Closest Points to Origin", "M", "NC150", "heap by distance", 15),
    (265, "Top K Frequent Words", "M", "", "heap with tie-breaking", 15),
    (266, "Find Median from Data Stream", "H", "B75", "two heaps", 15),
    (267, "Find K Pairs with Smallest Sums", "M", "TI150", "heap frontier expansion", 15),
    (268, "Smallest Range Covering Elements from K Lists", "H", "", "heap over K pointers", 15),
    (269, "Single-Threaded CPU", "M", "", "sort by time + heap by duration", 15),
    (270, "Minimum Cost to Connect Sticks $", "M", "", "Huffman-style merge", 15),
    (271, "Furthest Building You Can Reach", "M", "", "heap of the largest climbs", 15),
    (272, "Process Tasks Using Servers", "M", "", "two heaps (free / busy)", 15),
    (273, "Sliding Window Median", "H", "", "two heaps + lazy delete", 15),
    (274, "Design Twitter", "M", "NC150", "k-way merge of feeds", 15),
    (275, "[CSES] Sliding Window Median", "H", "", "sliding median with two multisets", 15),

    # Ch 16 (276-305)
    (276, "Maximum Depth of Binary Tree", "E", "B75", "basic recursion", 16),
    (277, "Invert Binary Tree", "E", "B75", "swap children recursively", 16),
    (278, "Same Tree", "E", "B75", "parallel traversal", 16),
    (279, "Symmetric Tree", "E", "TI150", "mirror recursion", 16),
    (280, "Subtree of Another Tree", "E", "B75", "match + traverse", 16),
    (281, "Diameter of Binary Tree", "E", "NC150", "height with a global best", 16),
    (282, "Balanced Binary Tree", "E", "NC150", "bottom-up return values", 16),
    (283, "Binary Tree Level Order Traversal", "M", "B75", "BFS by level", 16),
    (284, "Average of Levels in Binary Tree", "E", "TI150", "level sums and counts", 16),
    (285, "Binary Tree Right Side View", "M", "NC150", "BFS last-of-level", 16),
    (286, "Binary Tree Zigzag Level Order Traversal", "M", "TI150", "alternating direction", 16),
    (287, "Path Sum", "E", "TI150", "top-down state", 16),
    (288, "Path Sum II", "M", "", "backtracking paths", 16),
    (289, "Path Sum III", "M", "", "prefix sums on a tree", 16),
    (290, "Sum Root to Leaf Numbers", "M", "TI150", "pass the number down", 16),
    (291, "Count Good Nodes in Binary Tree", "M", "NC150", "pass max along the path", 16),
    (292, "Lowest Common Ancestor of a Binary Tree", "M", "TI150", "recursive LCA", 16),
    (293, "Construct Binary Tree from Preorder and Inorder Traversal", "M", "B75", "split by root index", 16),
    (294, "Construct Binary Tree from Inorder and Postorder Traversal", "M", "TI150", "root is the last postorder element", 16),
    (295, "Binary Tree Maximum Path Sum", "H", "B75", "downward gain with global max", 16),
    (296, "Serialize and Deserialize Binary Tree", "H", "B75", "preorder with null markers", 16),
    (297, "Flatten Binary Tree to Linked List", "M", "TI150", "reverse postorder / Morris", 16),
    (298, "Populating Next Right Pointers in Each Node II", "M", "TI150", "next pointers as an O(1) level queue", 16),
    (299, "Count Complete Tree Nodes", "M", "TI150", "height check + binary descent", 16),
    (300, "Binary Tree Inorder Traversal", "E", "", "iterative traversal with stack", 16),
    (301, "All Nodes Distance K in Binary Tree", "M", "", "parent map + BFS", 16),
    (302, "House Robber III", "M", "", "tree DP with two states", 16),
    (303, "Binary Tree Cameras", "H", "", "greedy states on a tree", 16),
    (304, "Vertical Order Traversal of a Binary Tree", "H", "", "coordinates + sorting", 16),
    (305, "Amount of Time for Binary Tree to Be Infected", "M", "", "tree to graph BFS", 16),

    # Ch 17 (306-320)
    (306, "Validate Binary Search Tree", "M", "B75", "bounds recursion", 17),
    (307, "Kth Smallest Element in a BST", "M", "B75", "inorder property", 17),
    (308, "Lowest Common Ancestor of a Binary Search Tree", "M", "B75", "use ordering to descend", 17),
    (309, "Insert into a Binary Search Tree", "M", "", "recursive insert", 17),
    (310, "Delete Node in a BST", "M", "", "three deletion cases", 17),
    (311, "Convert Sorted Array to Binary Search Tree", "E", "TI150", "balanced build", 17),
    (312, "Binary Search Tree Iterator", "M", "TI150", "controlled inorder with a stack", 17),
    (313, "Recover Binary Search Tree", "M", "", "find the two swapped nodes", 17),
    (314, "Trim a Binary Search Tree", "M", "", "prune using ordering", 17),
    (315, "Minimum Absolute Difference in BST", "E", "TI150", "adjacent values in inorder", 17),
    (316, "Unique Binary Search Trees", "M", "", "Catalan DP", 17),
    (317, "Two Sum IV - Input is a BST", "E", "", "iterator pair / set", 17),
    (318, "My Calendar I", "M", "", "ordered set for intervals", 17),
    (319, "Contains Duplicate III", "H", "", "ordered set / buckets", 17),
    (320, "Stock Price Fluctuation", "M", "", "ordered map + heap", 17),

    # Ch 18 (321-330)
    (321, "Implement Trie (Prefix Tree)", "M", "B75", "insert/search/startsWith", 18),
    (322, "Design Add and Search Words Data Structure", "M", "B75", "wildcard DFS on a trie", 18),
    (323, "Word Search II", "H", "B75", "trie + grid backtracking with pruning", 18),
    (324, "Replace Words", "M", "", "shortest root prefix", 18),
    (325, "Longest Word in Dictionary", "M", "", "trie with path validity", 18),
    (326, "Search Suggestions System", "M", "", "sorted prefix suggestions", 18),
    (327, "Palindrome Pairs", "H", "", "trie of reversed words", 18),
    (328, "Stream of Characters", "H", "", "reversed trie over a stream", 18),
    (329, "Prefix and Suffix Search", "H", "", "combined key trie", 18),
    (330, "Map Sum Pairs", "M", "", "subtree sums in a trie", 18),

    # Ch 19 (331-359)
    (331, "Number of Islands", "M", "B75", "DFS flood fill", 19),
    (332, "Max Area of Island", "M", "NC150", "DFS with area count", 19),
    (333, "Flood Fill", "E", "", "basic grid fill", 19),
    (334, "Rotting Oranges", "M", "NC150", "multi-source BFS", 19),
    (335, "Walls and Gates $", "M", "NC150", "multi-source BFS filling distances", 19),
    (336, "01 Matrix", "M", "", "multi-source BFS distances", 19),
    (337, "Pacific Atlantic Water Flow", "M", "B75", "reverse BFS from borders", 19),
    (338, "Surrounded Regions", "M", "NC150", "border-connected marking", 19),
    (339, "Number of Enclaves", "M", "", "remove border-reachable land", 19),
    (340, "Clone Graph", "M", "B75", "DFS/BFS with a map", 19),
    (341, "Number of Provinces", "M", "", "components", 19),
    (342, "Is Graph Bipartite", "M", "", "2-colouring", 19),
    (343, "Find if Path Exists in Graph", "E", "", "reachability", 19),
    (344, "Word Ladder", "H", "NC150", "BFS on implicit word graph", 19),
    (345, "Open the Lock", "M", "", "BFS on states", 19),
    (346, "Minimum Genetic Mutation", "M", "TI150", "BFS over one-letter mutations", 19),
    (347, "Shortest Path in Binary Matrix", "M", "", "8-direction BFS", 19),
    (348, "Snakes and Ladders", "M", "TI150", "BFS with board mapping", 19),
    (349, "Shortest Bridge", "M", "", "DFS then BFS expansion", 19),
    (350, "Bus Routes", "H", "", "BFS over routes not stops", 19),
    (351, "Making A Large Island", "H", "", "component sizes + merge check", 19),
    (352, "Shortest Path Visiting All Nodes", "H", "", "BFS over (node, mask)", 19),
    (353, "[CSES] Counting Rooms", "E", "", "count connected components of '.' cells with BFS/DFS", 19),
    (354, "[CSES] Labyrinth", "E", "", "BFS with path reconstruction", 19),
    (355, "[CSES] Monsters", "M", "", "two BFS races: monsters vs player", 19),
    (356, "[CSES] Building Roads", "E", "", "components then connect them with DSU", 19),
    (357, "[CSES] Message Route", "E", "", "shortest path with parent tracking", 19),
    (358, "[CSES] Building Teams", "E", "", "bipartite 2-colouring with BFS", 19),
    (359, "[CSES] Round Trip", "M", "", "cycle finding in an undirected graph with DFS", 19),

    # Ch 20 (360-389)
    (360, "Course Schedule", "M", "B75", "cycle detection in a directed graph", 20),
    (361, "Course Schedule II", "M", "NC150", "topological order (Kahn)", 20),
    (362, "Alien Dictionary $", "H", "B75", "build graph from ordering, toposort", 20),
    (363, "Parallel Courses III", "H", "", "DP over topological order", 20),
    (364, "Find Eventual Safe States", "M", "", "reverse graph toposort", 20),
    (365, "Number of Connected Components in an Undirected Graph $", "M", "B75", "DSU", 20),
    (366, "Graph Valid Tree $", "M", "B75", "DSU / edge-count + connectivity", 20),
    (367, "Redundant Connection", "M", "NC150", "DSU cycle edge", 20),
    (368, "Accounts Merge", "M", "", "DSU on strings", 20),
    (369, "Most Stones Removed with Same Row or Column", "M", "", "DSU on rows/columns", 20),
    (370, "Evaluate Division", "M", "TI150", "weighted graph / weighted DSU", 20),
    (371, "Network Delay Time", "M", "NC150", "Dijkstra", 20),
    (372, "Cheapest Flights Within K Stops", "M", "NC150", "Bellman-Ford by layers", 20),
    (373, "Path With Minimum Effort", "M", "", "Dijkstra on max-edge", 20),
    (374, "Swim in Rising Water", "H", "NC150", "Dijkstra / binary search + BFS", 20),
    (375, "Path with Maximum Probability", "M", "", "Dijkstra with products", 20),
    (376, "Find the City With the Smallest Number of Neighbors at a Threshold Distance", "M", "", "Floyd-Warshall", 20),
    (377, "Min Cost to Connect All Points", "M", "NC150", "Kruskal / Prim MST", 20),
    (378, "Optimize Water Distribution in a Village $", "H", "", "MST with a virtual node", 20),
    (379, "Find Critical and Pseudo-Critical Edges in Minimum Spanning Tree", "H", "", "MST edge criticality", 20),
    (380, "[CSES] Shortest Routes I", "E", "", "Dijkstra template with priority queue", 20),
    (381, "[CSES] Shortest Routes II", "M", "", "Floyd-Warshall template (n<=500)", 20),
    (382, "[CSES] High Score", "M", "", "Bellman-Ford / longest path, negative cycles", 20),
    (383, "[CSES] Cycle Finding", "M", "", "negative cycle output via Bellman-Ford", 20),
    (384, "[CSES] Flight Discount", "M", "", "Dijkstra on states (node, coupon used)", 20),
    (385, "[CSES] Investigation", "M", "", "Dijkstra tracking count, min/max edges", 20),
    (386, "[CSES] Course Schedule", "E", "", "toposort with Kahn's algorithm", 20),
    (387, "[CSES] Longest Flight Route", "M", "", "longest path in a DAG with topological DP", 20),
    (388, "[CSES] Road Reparation", "E", "", "Kruskal with DSU", 20),
    (389, "[CSES] Road Construction", "M", "", "DSU with component count and max size tracking", 20),

    # Ch 21 (390-407)
    (390, "Critical Connections in a Network", "H", "", "bridges via low-link", 21),
    (391, "Reconstruct Itinerary", "H", "NC150", "Hierholzer's Euler path", 21),
    (392, "Cracking the Safe", "H", "", "de Bruijn / Eulerian cycle", 21),
    (393, "Valid Arrangement of Pairs", "H", "", "Euler path in a directed graph", 21),
    (394, "Longest Cycle in a Graph", "H", "", "functional graph cycle", 21),
    (395, "Maximum Employees to Be Invited to a Meeting", "H", "", "functional graph + cycles", 21),
    (396, "[CSES] Flight Routes Check", "M", "", "strong connectivity check on graph and reverse", 21),
    (397, "[CSES] Planets and Kingdoms", "M", "", "SCC condensation (Kosaraju or Tarjan)", 21),
    (398, "[CSES] Giant Pizza", "H", "", "2-SAT via SCC implication graph", 21),
    (399, "[CSES] Coin Collector", "M", "", "DP on the SCC condensation DAG", 21),
    (400, "[CSES] Mail Delivery", "M", "", "Euler circuit (undirected) with Hierholzer", 21),
    (401, "[CSES] De Bruijn Sequence", "H", "", "Eulerian path over (n-1)-bit nodes", 21),
    (402, "[CSES] Teleporters Path", "M", "", "Euler path (directed) checking in/out degrees", 21),
    (403, "[CSES] Hamiltonian Flights", "H", "", "Hamiltonian paths with bitmask DP", 21),
    (404, "[CSES] Download Speed", "H", "", "max flow (Dinic) from 1 to n", 21),
    (405, "[CSES] Police Chase", "H", "", "min cut extraction via max flow + BFS", 21),
    (406, "[CSES] School Dance", "H", "", "bipartite matching via max flow / Hopcroft-Karp", 21),
    (407, "[CSES] Distinct Routes", "H", "", "edge-disjoint paths via max flow with unit capacities", 21),

    # Ch 22 (408-430)
    (408, "Kth Ancestor of a Tree Node", "H", "", "binary lifting", 22),
    (409, "Minimum Height Trees", "M", "", "tree centre by leaf trimming", 22),
    (410, "Sum of Distances in Tree", "H", "", "rerooting DP", 22),
    (411, "Longest Path With Different Adjacent Characters", "H", "", "tree DP with two best children", 22),
    (412, "Number of Nodes in the Sub-Tree With the Same Label", "M", "", "subtree frequency merge", 22),
    (413, "Difference Between Maximum and Minimum Price Sum", "H", "", "rerooting with best paths", 22),
    (414, "Collect Coins in a Tree", "H", "", "prune leaves then count edges", 22),
    (415, "Count Number of Possible Root Nodes", "H", "", "rerooting counts", 22),
    (416, "Minimum Edge Weight Equilibrium Queries in a Tree", "H", "", "LCA + path counts", 22),
    (417, "[CSES] Subordinates", "E", "", "subtree sizes via DFS", 22),
    (418, "[CSES] Tree Diameter", "E", "", "two BFS/DFS runs for tree diameter", 22),
    (419, "[CSES] Tree Distances I", "M", "", "distances via diameter endpoints", 22),
    (420, "[CSES] Tree Distances II", "M", "", "rerooting distance sums", 22),
    (421, "[CSES] Company Queries I", "M", "", "binary lifting table up[k][v]", 22),
    (422, "[CSES] Company Queries II", "M", "", "LCA via binary lifting or Euler tour", 22),
    (423, "[CSES] Distance Queries", "M", "", "distance = depth[u] + depth[v] - 2*depth[lca]", 22),
    (424, "[CSES] Counting Paths", "H", "", "path counting with difference on trees", 22),
    (425, "[CSES] Subtree Queries", "M", "", "Euler tour + Fenwick tree for subtree queries", 22),
    (426, "[CSES] Path Queries", "M", "", "path queries with Euler tour and Fenwick tree", 22),
    (427, "[CSES] Path Queries II", "H", "", "heavy-light decomposition + segment tree", 22),
    (428, "[CSES] Distinct Colors", "H", "", "small-to-large merging of sets or Euler tour + BIT", 22),
    (429, "[CSES] Finding a Centroid", "H", "", "centroid finding: walk to child with size > n/2", 22),
    (430, "[CSES] Fixed-Length Paths I", "H", "", "centroid decomposition with depth count array", 22),

    # Ch 23 (431-463)
    (431, "Climbing Stairs", "E", "B75", "first 1D recurrence", 23),
    (432, "House Robber", "M", "B75", "take/skip state", 23),
    (433, "House Robber II", "M", "B75", "circular reduction to two linear runs", 23),
    (434, "Min Cost Climbing Stairs", "E", "NC150", "cost recurrence", 23),
    (435, "Decode Ways", "M", "B75", "count with constraints", 23),
    (436, "Coin Change", "M", "B75", "unbounded min coins", 23),
    (437, "Coin Change II", "M", "NC150", "combinations (loop order)", 23),
    (438, "Word Break", "M", "B75", "prefix DP with a dictionary", 23),
    (439, "Longest Increasing Subsequence", "M", "B75", "O(n^2) then O(n log n)", 23),
    (440, "Delete and Earn", "M", "", "reduce to house robber", 23),
    (441, "Unique Paths II", "M", "TI150", "grid DP with obstacles", 23),
    (442, "Minimum Path Sum", "M", "TI150", "grid DP", 23),
    (443, "Triangle", "M", "TI150", "bottom-up rolling array", 23),
    (444, "Maximal Square", "M", "TI150", "2D dp from neighbours", 23),
    (445, "Dungeon Game", "H", "", "backward DP", 23),
    (446, "Cherry Pickup II", "H", "", "two walkers as one state", 23),
    (447, "Partition Equal Subset Sum", "M", "NC150", "0/1 subset sum", 23),
    (448, "Target Sum", "M", "NC150", "sum transformation to subset sum", 23),
    (449, "Last Stone Weight II", "M", "", "minimise difference via subset sum", 23),
    (450, "Combination Sum IV", "M", "B75", "permutations (loop order)", 23),
    (451, "Ones and Zeroes", "M", "", "2-D knapsack", 23),
    (452, "Longest Common Subsequence", "M", "B75", "2D LCS", 23),
    (453, "Edit Distance", "M", "NC150", "insert/delete/replace transitions", 23),
    (454, "Longest Palindromic Subsequence", "M", "", "interval/LCS with reverse", 23),
    (455, "[AtCoder] Educational DP A - Frog 1", "E", "", "1D DP warm-up: min energy jumps", 23),
    (456, "[AtCoder] Educational DP D - Knapsack 1", "E", "", "0/1 knapsack with 1D capacity iterate downward", 23),
    (457, "[AtCoder] Educational DP F - LCS", "E", "", "LCS with reconstruction", 23),
    (458, "[AtCoder] Educational DP H - Grid 1", "E", "", "grid paths counting mod 1e9+7", 23),
    (459, "[CSES] Dice Combinations", "E", "", "count sequences summing to n", 23),
    (460, "[CSES] Minimizing Coins", "E", "", "unbounded coin change for minimum coins", 23),
    (461, "[CSES] Coin Combinations II", "M", "", "combinations with order ignored (coins outer loop)", 23),
    (462, "[CSES] Book Shop", "M", "", "0/1 knapsack: maximize pages within price", 23),
    (463, "[CSES] Increasing Subsequence", "M", "", "LIS with tails array and binary search", 23),

    # Ch 24 (464-498)
    (464, "Best Time to Buy and Sell Stock with Cooldown", "M", "NC150", "state machine DP", 24),
    (465, "Best Time to Buy and Sell Stock III", "H", "TI150", "at most 2 transactions", 24),
    (466, "Best Time to Buy and Sell Stock IV", "H", "TI150", "k transactions", 24),
    (467, "Best Time to Buy and Sell Stock with Transaction Fee", "M", "", "hold/sold states", 24),
    (468, "Burst Balloons", "H", "NC150", "interval DP, choose the last", 24),
    (469, "Palindrome Partitioning II", "H", "", "prefix DP + palindrome table", 24),
    (470, "Distinct Subsequences", "H", "NC150", "counting subsequences", 24),
    (471, "Interleaving String", "M", "NC150", "2D boolean DP", 24),
    (472, "Regular Expression Matching", "H", "NC150", "pattern DP with *", 24),
    (473, "Wildcard Matching", "H", "", "pattern DP with * and ?", 24),
    (474, "Longest Increasing Path in a Matrix", "H", "NC150", "DFS + memo on a DAG", 24),
    (475, "Minimum Cost to Cut a Stick", "H", "", "interval DP", 24),
    (476, "Strange Printer", "H", "", "interval DP on strings", 24),
    (477, "Stone Game", "M", "", "game DP, score difference", 24),
    (478, "Predict the Winner", "M", "", "interval game DP", 24),
    (479, "Longest String Chain", "M", "", "DP over sorted lengths", 24),
    (480, "Russian Doll Envelopes", "H", "", "LIS after sorting", 24),
    (481, "Number of Longest Increasing Subsequence", "M", "", "LIS with counts", 24),
    (482, "Smallest Sufficient Team", "H", "", "bitmask DP over skills", 24),
    (483, "Count Special Integers", "H", "", "digit DP", 24),
    (484, "Numbers At Most N Given Digit Set", "H", "", "digit DP with tight flag", 24),
    (485, "Knight Probability in Chessboard", "M", "", "probability DP", 24),
    (486, "New 21 Game", "M", "", "sliding-window probability DP", 24),
    (487, "Super Egg Drop", "H", "", "DP with binary search optimisation", 24),
    (488, "[AtCoder] Educational DP E - Knapsack 2", "M", "", "knapsack with huge weights (value DP)", 24),
    (489, "[AtCoder] Educational DP J - Sushi", "M", "", "expected value DP over dish counts", 24),
    (490, "[AtCoder] Educational DP K - Stones", "M", "", "game DP: winning/losing states", 24),
    (491, "[AtCoder] Educational DP L - Deque", "M", "", "interval game DP score difference", 24),
    (492, "[AtCoder] Educational DP O - Matching", "M", "", "bitmask matching DP: O(N 2^N)", 24),
    (493, "[AtCoder] Educational DP P - Independent Set", "M", "", "tree DP: black/white independent sets", 24),
    (494, "[AtCoder] Educational DP S - Digit Sum", "M", "", "digit DP over K's digits mod D", 24),
    (495, "[CSES] Removal Game", "M", "", "interval game of score difference", 24),
    (496, "[CSES] Elevator Rides", "M", "", "bitmask over subsets: min rides and min weight", 24),
    (497, "[CSES] Counting Tilings", "H", "", "broken-profile DP over cells with column mask", 24),
    (498, "[CSES] Counting Numbers", "M", "", "digit DP: count numbers with no equal adjacent digits", 24),

    # Ch 25 (499-510)
    (499, "Longest Increasing Subsequence II", "H", "", "DP with a segment tree", 25),
    (500, "Constrained Subsequence Sum", "H", "", "DP with a monotonic deque", 25),
    (501, "Jump Game VI", "M", "", "deque-optimised DP window", 25),
    (502, "Maximum Profit in Job Scheduling", "H", "", "DP + binary search", 25),
    (503, "Minimum Total Distance Traveled", "H", "", "sorted DP / assignment", 25),
    (504, "Allocate Mailboxes", "H", "", "partition DP with cost table", 25),
    (505, "[CSES] Increasing Subsequence II", "M", "", "BIT-optimised DP over coordinate-compressed values", 25),
    (506, "[CSES] Monster Game I", "H", "", "convex hull trick query at s_i", 25),
    (507, "[CSES] Monster Game II", "H", "", "Li Chao tree when slopes/queries not monotone", 25),
    (508, "[CSES] Subarray Squares", "H", "", "divide and conquer optimisation on monotone split", 25),
    (509, "[CSES] Houses and Schools", "H", "", "D&C DP with cost function from prefix sums", 25),
    (510, "[CSES] Knuth Division", "H", "", "Knuth optimisation: optimal splits monotone in both indices", 25),

    # Ch 26 (511-533)
    (511, "Range Sum Query - Mutable", "M", "", "Fenwick tree", 26),
    (512, "Range Sum Query 2D - Mutable $", "M", "", "2D Fenwick", 26),
    (513, "Create Sorted Array through Instructions", "H", "", "BIT counting on values", 26),
    (514, "Count of Range Sum", "H", "", "BIT / merge sort on prefix sums", 26),
    (515, "Falling Squares", "H", "", "segment tree with range max", 26),
    (516, "My Calendar III", "H", "", "segment tree with range add", 26),
    (517, "Range Module", "H", "", "interval set with a segment tree", 26),
    (518, "Rectangle Area II", "H", "", "sweep line + segment tree cover", 26),
    (519, "Number of Flowers in Full Bloom", "H", "", "offline sort + BIT/difference", 26),
    (520, "Longest Substring of One Repeating Character", "H", "", "segment tree merge of runs", 26),
    (521, "[CSES] Dynamic Range Sum Queries", "E", "", "Fenwick tree point update and range sum", 26),
    (522, "[CSES] Dynamic Range Minimum Queries", "M", "", "segment tree min with point update", 26),
    (523, "[CSES] Range Update Queries", "M", "", "Fenwick over difference array: range add, point query", 26),
    (524, "[CSES] Range Updates and Sums", "H", "", "lazy propagation (add + assign)", 26),
    (525, "[CSES] Polynomial Queries", "H", "", "lazy tags with arithmetic progression formula", 26),
    (526, "[CSES] Hotel Queries", "M", "", "segment tree descent to leftmost hotel", 26),
    (527, "[CSES] Salary Queries", "H", "", "offline compression + Fenwick tree", 26),
    (528, "[CSES] List Removals", "H", "", "order statistics with BIT binary descent", 26),
    (529, "[CSES] Subarray Sum Queries", "H", "", "segment tree node storing max prefix/suffix/subarray", 26),
    (530, "[CSES] Static Range Minimum Queries", "M", "", "sparse table RMQ in O(1) query", 26),
    (531, "[CSES] Distinct Values Queries", "H", "", "offline queries with BIT or Mo's algorithm", 26),
    (532, "[CSES] Increasing Array Queries", "H", "", "prefix + binary lifting over monotonic stack", 26),
    (533, "[CSES] Range Queries and Copies", "H", "", "persistent segment tree", 26),

    # Ch 27 (534-548)
    (534, "Shortest Palindrome", "H", "", "KMP on s + '#' + reverse", 27),
    (535, "Longest Happy Prefix", "H", "", "prefix function directly", 27),
    (536, "Longest Duplicate Substring", "H", "", "rolling hash + binary search", 27),
    (537, "Sum of Scores of Built Strings", "H", "", "Z-function", 27),
    (538, "Count Prefix and Suffix Pairs II", "H", "", "Z / hashing / trie", 27),
    (539, "Number of Distinct Substrings in a String $", "M", "", "suffix structure / hashing", 27),
    (540, "[CSES] String Matching", "E", "", "pattern matching with KMP or Z-algorithm", 27),
    (541, "[CSES] Finding Borders", "M", "", "borders via prefix function failure links", 27),
    (542, "[CSES] Finding Periods", "M", "", "periods: p is period if n-p is border length", 27),
    (543, "[CSES] Longest Palindrome", "M", "", "Manacher's algorithm in O(n)", 27),
    (544, "[CSES] Minimal Rotation", "M", "", "Booth's algorithm / Duval / suffix array", 27),
    (545, "[CSES] Required Substring", "H", "", "KMP automaton DP", 27),
    (546, "[CSES] Distinct Substrings", "H", "", "suffix array + LCP: n(n+1)/2 - sum(LCP)", 27),
    (547, "[CSES] Finding Patterns", "H", "", "Aho-Corasick or suffix array with binary search", 27),
    (548, "[CSES] String Transform", "H", "", "Burrows-Wheeler transform inverse", 27),

    # Ch 28 (549-563)
    (549, "Erect the Fence", "H", "", "convex hull", 28),
    (550, "Valid Square", "M", "", "distance / vectors", 28),
    (551, "Detect Squares", "M", "NC150", "hash counts + diagonal search", 28),
    (552, "Rectangle Area", "M", "", "inclusion of overlap", 28),
    (553, "Minimum Area Rectangle", "M", "", "hash points, diagonals", 28),
    (554, "Perfect Rectangle", "H", "", "corner-count argument", 28),
    (555, "Maximum Number of Visible Points", "H", "", "angular sweep", 28),
    (556, "[CSES] Point Location Test", "E", "", "orientation via cross product (p2 - p1) x (p - p1)", 28),
    (557, "[CSES] Line Segment Intersection", "M", "", "segment intersection with bounding boxes & orientation", 28),
    (558, "[CSES] Polygon Area", "E", "", "shoelace formula with cross products", 28),
    (559, "[CSES] Point in Polygon", "M", "", "ray casting with explicit boundary check", 28),
    (560, "[CSES] Polygon Lattice Points", "M", "", "Pick's theorem: A = I + B/2 - 1", 28),
    (561, "[CSES] Minimum Euclidean Distance", "H", "", "closest pair via sweep line / D&C in O(n log n)", 28),
    (562, "[CSES] Convex Hull", "M", "", "Andrew's monotone chain", 28),
    (563, "[CSES] Area of Rectangles", "H", "", "sweep line + segment tree of covered length", 28),

    # Ch 29 (564-574)
    (564, "Nim Game", "E", "", "small-case analysis: n % 4 != 0", 29),
    (565, "Divisor Game", "E", "", "parity pattern: Alice wins iff n is even", 29),
    (566, "Can I Win", "M", "", "bitmask minimax", 29),
    (567, "Stone Game III", "H", "", "suffix DP for score difference", 29),
    (568, "Guess Number Higher or Lower II", "M", "", "minimax interval DP", 29),
    (569, "Flip Game II $", "M", "", "backtracking with memo", 29),
    (570, "[CSES] Stick Game", "E", "", "win/lose DP for subtraction game", 29),
    (571, "[CSES] Nim Game I", "M", "", "Nim and XOR: non-zero XOR means first player wins", 29),
    (572, "[CSES] Nim Game II", "M", "", "Nim with piles: x mod 4 residues XOR", 29),
    (573, "[CSES] Stair Game", "M", "", "staircase Nim: XOR odd-step piles", 29),
    (574, "[CSES] Grundy's Game", "H", "", "Grundy numbers: mex over split states", 29),

    # Ch 30 (575-589)
    (575, "Design HashMap", "E", "", "chaining/open addressing", 30),
    (576, "Design Browser History", "M", "", "stack/array pointer", 30),
    (577, "Design Circular Queue", "M", "", "ring buffer", 30),
    (578, "Design Hit Counter $", "M", "", "queue/window of timestamps", 30),
    (579, "Logger Rate Limiter $", "E", "", "map of last timestamp", 30),
    (580, "Design Underground System", "M", "", "two maps, averages", 30),
    (581, "Snapshot Array", "M", "", "versioned values with binary search", 30),
    (582, "Flatten Nested List Iterator $", "M", "", "stack-based iterator", 30),
    (583, "Peeking Iterator", "M", "", "caching the next element", 30),
    (584, "LFU Cache", "H", "", "frequency buckets + linked lists", 30),
    (585, "All O`one Data Structure", "H", "", "linked list of count buckets", 30),
    (586, "Design Search Autocomplete System $", "H", "", "trie + top-3", 30),
    (587, "Design In-Memory File System $", "H", "", "trie of directories", 30),
    (588, "Design a Text Editor", "H", "", "two stacks / gap buffer", 30),
    (589, "Design Skiplist", "H", "", "probabilistic levels", 30),

    # Ch 31 (590-608)
    (590, "Game of Life", "M", "TI150", "in-place state encoding", 31),
    (591, "Robot Bounded In Circle", "M", "", "simulation invariant", 31),
    (592, "Text Justification", "H", "TI150", "greedy line packing", 31),
    (593, "Integer to English Words", "H", "", "structured simulation", 31),
    (594, "Push Dominoes", "M", "", "two-pass forces", 31),
    (595, "Beautiful Array", "M", "", "divide and conquer construction", 31),
    (596, "Construct the Lexicographically Largest Valid Sequence", "M", "", "backtracking construction", 31),
    (597, "Find Permutation $", "M", "", "greedy construction from a pattern", 31),
    (598, "[CSES] Number Spiral", "E", "", "layer max(x, y), parity gives direction, closed form", 31),
    (599, "[CSES] Two Knights", "E", "", "closed form counting: C(k^2, 2) - 4(k-1)(k-2)", 31),
    (600, "[CSES] Two Sets", "E", "", "constructive partition: greedily fill from largest down", 31),
    (601, "[CSES] Coin Piles", "E", "", "invariant: (a+b)%3 == 0 and 2a>=b and 2b>=a", 31),
    (602, "[CSES] Palindrome Reorder", "E", "", "rearrangement constraints: at most one odd count", 31),
    (603, "[CSES] Gray Code", "E", "", "Gray code construction: i ^ (i >> 1)", 31),
    (604, "[CSES] String Reorder", "M", "", "greedy lexicographic construction checking feasibility", 31),
    (605, "[CSES] Digit Queries", "M", "", "digit-length counting: 9 * 10^(d-1) * d", 31),
    (606, "[CSES] Chess Tournament", "M", "", "Havel-Hakimi style construction", 31),
    (607, "[CSES] Hidden Integer", "E", "", "interactive binary search on [1, 1e9] with flush", 31),
    (608, "[CSES] Hidden Permutation", "M", "", "interactive permutation recovery halving candidates", 31),

    # Ch 32 (609-610)
    (609, "[LibChk] Convolution Mod", "E", "", "NTT polynomial multiplication mod 998244353", 32),
    (610, "[LibChk] Convolution Mod 10^9+7", "M", "", "arbitrary-modulus FFT with 3 primes + CRT", 32)
]

# Map chapter metadata
ch_dict = {c["id"]: c for c in chapters_meta}

problems = []
for p in raw_problems:
    pid, title, lvl, lst, hint, ch_id = p
    ch_info = ch_dict[ch_id]
    
    # Platform
    if title.startswith("[CSES]"):
        plat = "CSES"
    elif title.startswith("[AtCoder]"):
        plat = "AtCoder"
    elif title.startswith("[LibChk]"):
        plat = "Library Checker"
    else:
        plat = "LeetCode"
        
    is_premium = "$" in title
    clean_title = title.replace("$", "").strip()

    # Lists
    lists = []
    if "B75" in lst:
        lists.append("Blind 75")
    if "NC150" in lst:
        lists.append("NeetCode 150")
    if "TI150" in lst:
        lists.append("Top Interview 150")

    prob_obj = {
        "id": pid,
        "title": clean_title,
        "raw_title": title,
        "chapter_id": ch_id,
        "chapter_name": ch_info["name"],
        "phase": ch_info["phase"],
        "level": lvl,
        "level_full": "Easy" if lvl == "E" else ("Medium" if lvl == "M" else "Hard"),
        "lists": lists,
        "hint": hint,
        "platform": plat,
        "url": get_url(title),
        "is_premium": is_premium
    }
    problems.append(prob_obj)

print(f"Generated {len(problems)} problems. Verifying problem count: {len(problems)} == 610.")
assert len(problems) == 610, f"Expected 610 problems, got {len(problems)}"

with open("data/problems.json", "w", encoding="utf-8") as f:
    json.dump(problems, f, indent=2, ensure_ascii=False)

with open("data/chapters.json", "w", encoding="utf-8") as f:
    json.dump(chapters_meta, f, indent=2, ensure_ascii=False)

print("Successfully wrote data/problems.json and data/chapters.json!")
