#include <iostream>
#include <chrono>

using namespace std;

// Iterative factorial
long long factorial_iterative(int n) {
    long long result = 1;
    for (int i = 1; i <= n; ++i) {
        result *= i;
    }
    return result;
}

// Recursive factorial
long long factorial_recursive(int n) {
    if (n == 0) return 1;
    return n * factorial_recursive(n - 1);
}

int main() {
    int num = 20;

    auto start_iter = chrono::high_resolution_clock::now();
    cout << "Iterative Factorial of " << num << ": " << factorial_iterative(num) << endl;
    auto end_iter = chrono::high_resolution_clock::now();
    cout << "Iterative Execution Time: " << chrono::duration_cast<chrono::microseconds>(end_iter - start_iter).count() << " microseconds" << endl;

    auto start_rec = chrono::high_resolution_clock::now();
    cout << "Recursive Factorial of " << num << ": " << factorial_recursive(num) << endl;
    auto end_rec = chrono::high_resolution_clock::now();
    cout << "Recursive Execution Time: " << chrono::duration_cast<chrono::microseconds>(end_rec - start_rec).count() << " microseconds" << endl;

    return 0;
}
