def wordBreak(s: str, wordDict: list[str]) -> bool:
    word_set = set(wordDict)  # O(1) lookups
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True  # base case

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break

    return dp[n]

if __name__ == "__main__":
    s = input().strip()
    wd = input().strip().split()
    print(str(wordBreak(s, wd)).lower())