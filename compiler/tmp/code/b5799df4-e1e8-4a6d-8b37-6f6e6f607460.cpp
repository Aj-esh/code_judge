#include <iostream>
#include <vector>

int main() {
    int n;
    std::cin >> n; // Read the integer from the first line of input

    std::vector<int> nums(n);
    for (int i = 0; i < n; ++i) {
        std::cin >> nums[i]; // Read the list of integers from the second line of input
    }

    // Calculate the expected sum of all numbers from 0 to n
    int expected_sum = n * (n + 1) / 2;

    // Calculate the actual sum of the numbers in the list
    int actual_sum = 0;
    for (int num : nums) {
        actual_sum += num;
    }

    // The missing number is the difference between the expected sum and the actual sum
    int missing_number = expected_sum - actual_sum;

    // Output the missing number
    std::cout << missing_number << std::endl;

    return 0;
}