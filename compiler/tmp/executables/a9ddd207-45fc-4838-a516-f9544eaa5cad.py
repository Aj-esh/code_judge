def find_missing_number(nums):
    n = len(nums)
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(nums)
    missing_number = expected_sum - actual_sum
    return missing_number

# Take input from the console
nums = list(map(int, input_str.split()))
# Output the result to the console
print(find_missing_number(nums))