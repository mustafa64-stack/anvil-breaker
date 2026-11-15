# app/sheets/sheets_loader.py
import json
import os
import re

def slugify(title):
    clean = re.sub(r'\[.*?\]', '', title)
    clean = clean.replace('$', '').strip()
    clean = clean.replace("`", "")
    clean = clean.replace("'", "")
    clean = clean.replace('"', '')
    clean = re.sub(r'[^a-zA-Z0-9\s-]', '', clean)
    clean = re.sub(r'[\s_]+', '-', clean).lower()
    return clean.strip('-')

def get_striver_sde_sheet():
    raw_data = [
        # Day 1: Arrays
        ("Set Matrix Zeroes", "Arrays", "M", "https://leetcode.com/problems/set-matrix-zeroes/", "O(1) space with first row/col as flags"),
        ("Pascal's Triangle", "Arrays", "E", "https://leetcode.com/problems/pascals-triangle/", "Row generation using binomial combination or previous row addition"),
        ("Next Permutation", "Arrays", "M", "https://leetcode.com/problems/next-permutation/", "Find pivot, swap with next greater, reverse suffix"),
        ("Maximum Subarray", "Arrays", "M", "https://leetcode.com/problems/maximum-subarray/", "Kadane's algorithm tracking max ending here and global max"),
        ("Sort Colors", "Arrays", "M", "https://leetcode.com/problems/sort-colors/", "Dutch National Flag 3-pointer partition (low, mid, high)"),
        ("Best Time to Buy and Sell Stock", "Arrays", "E", "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/", "Track running minimum price, maximize difference"),
        
        # Day 2: Arrays Part-II
        ("Rotate Image", "Arrays", "M", "https://leetcode.com/problems/rotate-image/", "Transpose matrix then reverse each row"),
        ("Merge Intervals", "Arrays", "M", "https://leetcode.com/problems/merge-intervals/", "Sort by start time, merge overlapping"),
        ("Merge Sorted Array", "Arrays", "E", "https://leetcode.com/problems/merge-sorted-array/", "Fill from the back using three pointers"),
        ("Find the Duplicate Number", "Arrays", "M", "https://leetcode.com/problems/find-the-duplicate-number/", "Floyd's Tortoise and Hare cycle detection on implicit linked list"),
        ("Repeat and Missing Number", "Arrays", "M", "https://www.interviewbit.com/problems/repeat-and-missing-number-array/", "Sum and sum of squares equations or XOR division"),
        ("Inversion of Array", "Arrays", "M", "https://www.geeksforgeeks.org/inversion-count-in-array-using-merge-sort/", "Modified merge sort counting cross inversions"),

        # Day 3: Arrays/Math
        ("Search a 2D Matrix", "Binary Search", "M", "https://leetcode.com/problems/search-a-2d-matrix/", "Flatten matrix to 1D index: row=mid/col, col=mid%col"),
        ("Pow(x, n)", "Math", "M", "https://leetcode.com/problems/powx-n/", "Binary exponentiation dividing power by 2 each step"),
        ("Majority Element", "Arrays", "E", "https://leetcode.com/problems/majority-element/", "Boyer-Moore Voting Algorithm"),
        ("Majority Element II", "Arrays", "M", "https://leetcode.com/problems/majority-element-ii/", "Extended Boyer-Moore with two candidate counters"),
        ("Unique Paths", "Dynamic Programming", "M", "https://leetcode.com/problems/unique-paths/", "Combinatorics: C(m+n-2, m-1) or 2D DP grid"),
        ("Reverse Pairs", "Sorting", "H", "https://leetcode.com/problems/reverse-pairs/", "Modified merge sort counting pairs before merge"),

        # Day 4: Hashing
        ("Two Sum", "Hashing", "E", "https://leetcode.com/problems/two-sum/", "Hash map storing complement target - num"),
        ("4Sum", "Two Pointers", "M", "https://leetcode.com/problems/4sum/", "Sort, fix two pointers, two-pointer scan for remaining two"),
        ("Longest Consecutive Sequence", "Hashing", "M", "https://leetcode.com/problems/longest-consecutive-sequence/", "Hash set, check if num-1 exists before starting chain"),
        ("Largest Subarray with 0 Sum", "Hashing", "M", "https://www.geeksforgeeks.org/find-the-largest-subarray-with-0-sum/", "Prefix sum with hash map of first seen index"),
        ("Subarray with given XOR K", "Hashing", "M", "https://www.interviewbit.com/problems/subarray-with-given-xor/", "Prefix XOR with frequency hash map: xr ^ k"),
        ("Longest Substring Without Repeating Characters", "Sliding Window", "M", "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "Sliding window with character index hash map"),

        # Day 5: Linked List
        ("Reverse Linked List", "Linked List", "E", "https://leetcode.com/problems/reverse-linked-list/", "Iterative three-pointer (prev, curr, next) reversal"),
        ("Middle of the Linked List", "Linked List", "E", "https://leetcode.com/problems/middle-of-the-linked-list/", "Slow and fast pointers"),
        ("Merge Two Sorted Lists", "Linked List", "E", "https://leetcode.com/problems/merge-two-sorted-lists/", "Dummy head iterative merge"),
        ("Remove Nth Node From End of List", "Linked List", "M", "https://leetcode.com/problems/remove-nth-node-from-end-of-list/", "Two pointers n nodes apart"),
        ("Add Two Numbers", "Linked List", "M", "https://leetcode.com/problems/add-two-numbers/", "Digit addition with carry propagation"),
        ("Delete Node in a Linked List", "Linked List", "M", "https://leetcode.com/problems/delete-node-in-a-linked-list/", "Copy next node's value and bypass it"),

        # Day 6: Linked List Part-II
        ("Intersection of Two Linked Lists", "Linked List", "E", "https://leetcode.com/problems/intersection-of-two-linked-lists/", "Pointer swap upon reaching end to equalize path length"),
        ("Linked List Cycle", "Linked List", "E", "https://leetcode.com/problems/linked-list-cycle/", "Floyd's cycle-finding slow/fast pointer"),
        ("Reverse Nodes in k-Group", "Linked List", "H", "https://leetcode.com/problems/reverse-nodes-in-k-group/", "Check k nodes ahead, reverse k-group, recurse or iterate"),
        ("Palindrome Linked List", "Linked List", "E", "https://leetcode.com/problems/palindrome-linked-list/", "Find middle, reverse second half, compare halves"),
        ("Linked List Cycle II", "Linked List", "M", "https://leetcode.com/problems/linked-list-cycle-ii/", "Floyd's algorithm: move one pointer to head, meet at cycle start"),
        ("Flattening of a Linked List", "Linked List", "M", "https://www.geeksforgeeks.org/flattening-a-linked-list/", "Merge two sorted lists recursively from the tail"),

        # Day 7: Linked List and Arrays
        ("Rotate List", "Linked List", "M", "https://leetcode.com/problems/rotate-list/", "Connect tail to head (circle), cut at length - k%length"),
        ("Copy List with Random Pointer", "Linked List", "M", "https://leetcode.com/problems/copy-list-with-random-pointer/", "Interleave cloned nodes between originals, set randoms, detach"),
        ("3Sum", "Two Pointers", "M", "https://leetcode.com/problems/3sum/", "Sort array, fix one element, two-pointer scan skipping duplicates"),
        ("Trapping Rain Water", "Two Pointers", "H", "https://leetcode.com/problems/trapping-rain-water/", "Two pointers with left_max and right_max"),
        ("Remove Duplicates from Sorted Array", "Two Pointers", "E", "https://leetcode.com/problems/remove-duplicates-from-sorted-array/", "Slow write pointer incremented on distinct elements"),
        ("Max Consecutive Ones", "Arrays", "E", "https://leetcode.com/problems/max-consecutive-ones/", "Single pass tracking current streak and max streak"),

        # Day 8: Greedy
        ("N meetings in one room", "Greedy", "E", "https://www.geeksforgeeks.org/activity-selection-problem-greedy-algo-1/", "Sort by end time, pick next non-overlapping meeting"),
        ("Minimum Platforms", "Greedy", "M", "https://www.geeksforgeeks.org/minimum-number-platforms-required-railwaybus-station/", "Sort arrivals and departures separately, two-pointer scan"),
        ("Job Sequencing Problem", "Greedy", "M", "https://www.geeksforgeeks.org/job-sequencing-problem/", "Sort by profit descending, slot into latest available day"),
        ("Fractional Knapsack", "Greedy", "M", "https://www.geeksforgeeks.org/fractional-knapsack-problem/", "Sort by value/weight ratio descending, greedily take fractions"),
        ("Find Minimum Number of Coins", "Greedy", "E", "https://www.geeksforgeeks.org/find-minimum-number-of-coins-that-make-a-change/", "Greedy selection for canonical coin denominations"),

        # Day 9: Recursion
        ("Subset Sums", "Recursion", "E", "https://www.geeksforgeeks.org/subset-sums/", "Include/exclude recursion tree"),
        ("Subsets II", "Backtracking", "M", "https://leetcode.com/problems/subsets-ii/", "Sort first, skip duplicates at the same depth"),
        ("Combination Sum", "Backtracking", "M", "https://leetcode.com/problems/combination-sum/", "Unbounded element reuse with index tracking"),
        ("Combination Sum II", "Backtracking", "M", "https://leetcode.com/problems/combination-sum-ii/", "Use each element once, sort and skip duplicates"),
        ("Palindrome Partitioning", "Backtracking", "M", "https://leetcode.com/problems/palindrome-partitioning/", "Partition at index i if prefix is palindrome"),
        ("Permutation Sequence", "Recursion", "H", "https://leetcode.com/problems/permutation-sequence/", "Factorial number system / Lehmer code digit selection"),

        # Day 10: Backtracking
        ("Permutations", "Backtracking", "M", "https://leetcode.com/problems/permutations/", "Used array or in-place swapping"),
        ("N-Queens", "Backtracking", "H", "https://leetcode.com/problems/n-queens/", "Row by row placement with col and diagonal sets"),
        ("Sudoku Solver", "Backtracking", "H", "https://leetcode.com/problems/sudoku-solver/", "Constraint propagation / empty cell recursion"),
        ("M-Coloring Problem", "Backtracking", "M", "https://www.geeksforgeeks.org/m-coloring-problem-backtracking-5/", "Try coloring vertex with 1..m, check neighbors, recurse"),
        ("Rat in a Maze Problem", "Backtracking", "M", "https://www.geeksforgeeks.org/rat-in-a-maze-backtracking-2/", "4-directional grid DFS with visited backtracking"),
        ("Word Break", "Dynamic Programming", "M", "https://leetcode.com/problems/word-break/", "DP array where dp[i] is true if prefix can be segmented"),

        # Day 11: Binary Search
        ("Nth Root of a Number", "Binary Search", "E", "https://www.geeksforgeeks.org/calculating-n-th-real-root-using-binary-search/", "Binary search on range [1, m] with multiplication check"),
        ("Search in Rotated Sorted Array", "Binary Search", "M", "https://leetcode.com/problems/search-in-rotated-sorted-array/", "Identify which half is strictly sorted"),
        ("Single Element in a Sorted Array", "Binary Search", "M", "https://leetcode.com/problems/single-element-in-a-sorted-array/", "Binary search on index parity"),
        ("Median of Two Sorted Arrays", "Binary Search", "H", "https://leetcode.com/problems/median-of-two-sorted-arrays/", "Binary search partition on the smaller array"),
        ("K-th Element of Two Sorted Arrays", "Binary Search", "M", "https://www.geeksforgeeks.org/k-th-element-two-sorted-arrays/", "Partition binary search with k elements in left half"),
        ("Allocate Books", "Binary Search", "M", "https://www.interviewbit.com/problems/allocate-books/", "Binary search on answer: range [max_element, sum]"),
        ("Aggressive Cows", "Binary Search", "M", "https://www.spoj.com/problems/AGGRCOW/", "Binary search on minimum distance with greedy check"),

        # Day 12: Heaps
        ("Kth Largest Element in an Array", "Heaps", "M", "https://leetcode.com/problems/kth-largest-element-in-an-array/", "Min-heap of size K or Quickselect"),
        ("Find Median from Data Stream", "Heaps", "H", "https://leetcode.com/problems/find-median-from-data-stream/", "Two heaps: max-heap for lower half, min-heap for upper half"),
        ("Top K Frequent Elements", "Heaps", "M", "https://leetcode.com/problems/top-k-frequent-elements/", "Frequency map + bucket sort or min-heap"),

        # Day 13: Stacks and Queues
        ("Implement Queue using Stacks", "Stack", "E", "https://leetcode.com/problems/implement-queue-using-stacks/", "Amortized O(1) with two stacks"),
        ("Valid Parentheses", "Stack", "E", "https://leetcode.com/problems/valid-parentheses/", "Stack push opens, pop and match closes"),
        ("Next Greater Element I", "Stack", "E", "https://leetcode.com/problems/next-greater-element-i/", "Monotonic decreasing stack"),
        ("Largest Rectangle in Histogram", "Stack", "H", "https://leetcode.com/problems/largest-rectangle-in-histogram/", "Monotonic stack tracking left/right boundaries"),
        ("Sliding Window Maximum", "Queue", "H", "https://leetcode.com/problems/sliding-window-maximum/", "Monotonic deque of indices"),
        ("Min Stack", "Stack", "M", "https://leetcode.com/problems/min-stack/", "Store (val, min_so_far) pairs or diff formula"),
        ("Rotting Oranges", "BFS", "M", "https://leetcode.com/problems/rotting-oranges/", "Multi-source BFS from all initial rotten oranges"),
        ("Online Stock Span", "Stack", "M", "https://leetcode.com/problems/online-stock-span/", "Monotonic stack storing (price, span)"),

        # Day 14: Trees & BST
        ("Binary Tree Inorder Traversal", "Binary Tree", "E", "https://leetcode.com/problems/binary-tree-inorder-traversal/", "Left, root, right (Morris or Stack)"),
        ("Maximum Depth of Binary Tree", "Binary Tree", "E", "https://leetcode.com/problems/maximum-depth-of-binary-tree/", "1 + max(depth(left), depth(right))"),
        ("Diameter of Binary Tree", "Binary Tree", "E", "https://leetcode.com/problems/diameter-of-binary-tree/", "Postorder height calculation updating global diameter"),
        ("Balanced Binary Tree", "Binary Tree", "E", "https://leetcode.com/problems/balanced-binary-tree/", "Bottom-up height return with -1 flag if unbalanced"),
        ("Lowest Common Ancestor of a Binary Tree", "Binary Tree", "M", "https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/", "Postorder search: return root if p or q found"),
        ("Binary Tree Level Order Traversal", "Binary Tree", "M", "https://leetcode.com/problems/binary-tree-level-order-traversal/", "Queue BFS with level size loop"),
        ("Validate Binary Search Tree", "BST", "M", "https://leetcode.com/problems/validate-binary-search-tree/", "Pass (min_val, max_val) bounds down recursion"),
        ("Kth Smallest Element in a BST", "BST", "M", "https://leetcode.com/problems/kth-smallest-element-in-a-bst/", "Inorder traversal stops at k-th step"),

        # Day 15: Graphs & DP
        ("Number of Islands", "Graphs", "M", "https://leetcode.com/problems/number-of-islands/", "Grid DFS/BFS flood-fill marking visited"),
        ("Clone Graph", "Graphs", "M", "https://leetcode.com/problems/clone-graph/", "DFS/BFS with hash map from original to clone"),
        ("Course Schedule", "Graphs", "M", "https://leetcode.com/problems/course-schedule/", "Cycle detection in directed graph with Kahn's or DFS"),
        ("Network Delay Time", "Graphs", "M", "https://leetcode.com/problems/network-delay-time/", "Dijkstra's shortest path with priority queue"),
        ("Climbing Stairs", "Dynamic Programming", "E", "https://leetcode.com/problems/climbing-stairs/", "Fibonacci DP: dp[i] = dp[i-1] + dp[i-2]"),
        ("Coin Change", "Dynamic Programming", "M", "https://leetcode.com/problems/coin-change/", "Unbounded knapsack DP: dp[a] = min(dp[a], 1 + dp[a - c])"),
        ("Longest Increasing Subsequence", "Dynamic Programming", "M", "https://leetcode.com/problems/longest-increasing-subsequence/", "O(N log N) binary search on tails array"),
        ("Longest Common Subsequence", "Dynamic Programming", "M", "https://leetcode.com/problems/longest-common-subsequence/", "2D DP matching characters: 1 + dp[i-1][j-1]"),
        ("0-1 Knapsack Problem", "Dynamic Programming", "M", "https://www.geeksforgeeks.org/0-1-knapsack-problem-dp-10/", "1D capacity loop downwards from W to weight"),
        ("Edit Distance", "Dynamic Programming", "M", "https://leetcode.com/problems/edit-distance/", "2D DP on insert, delete, replace transitions")
    ]

    sheet = []
    for idx, (title, topic, lvl, url, hint) in enumerate(raw_data, 1):
        sheet.append({
            "id": idx,
            "title": title,
            "chapter_name": topic,
            "level": lvl,
            "level_full": "Easy" if lvl == "E" else ("Medium" if lvl == "M" else "Hard"),
            "lists": ["Striver SDE"],
            "hint": hint,
            "platform": "LeetCode" if "leetcode" in url else "InterviewBit",
            "url": url,
            "is_premium": False
        })
    return sheet

def get_neetcode_150_sheet():
    # Load from the Core Path where NC150 is tagged
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    prob_file = os.path.join(base_dir, "data", "problems.json")
    if os.path.exists(prob_file):
        with open(prob_file, "r", encoding="utf-8") as f:
            all_probs = json.load(f)
        nc_probs = [p for p in all_probs if any("NeetCode 150" in l or "Blind 75" in l for l in p.get("lists", []))]
        # Re-index
        for idx, p in enumerate(nc_probs, 1):
            p_copy = dict(p)
            p_copy["id"] = idx
            nc_probs[idx - 1] = p_copy
        return nc_probs
    return []

def get_blind_75_sheet():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    prob_file = os.path.join(base_dir, "data", "problems.json")
    if os.path.exists(prob_file):
        with open(prob_file, "r", encoding="utf-8") as f:
            all_probs = json.load(f)
        b75_probs = [p for p in all_probs if any("Blind 75" in l for l in p.get("lists", []))]
        for idx, p in enumerate(b75_probs, 1):
            p_copy = dict(p)
            p_copy["id"] = idx
            b75_probs[idx - 1] = p_copy
        return b75_probs
    return []

