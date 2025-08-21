def find_missing_number(nums):
    n = len(nums)
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(nums)
    return expected_sum - actual_sum

# Take input from the console
input_str = input()
nums = list(map(int, input_str.split()))
# Output the result to the console
print(find_missing_number(nums))