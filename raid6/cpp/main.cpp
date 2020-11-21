#include <vector>
#include <iostream>
#include <cstring>
#include <chrono>
#include <set>
#include "RSCode.h"

class Test {
private:
    std::vector<unsigned char> src, encoded, decoded;
    size_t size = 0;

public:
    void testRSCode(unsigned char n, unsigned char k, size_t times) {
        RSCode rsCode(n, k);
        size_t pieceSize = size / k;
        if (size % k > 0) {
            pieceSize++;
        }
        std::cout << size << "," << (int) n << "," << (int) k << "," << times << ",";
        auto start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < times; i++) {
            rsCode.encode(pieceSize, src.data(), src.data() + k * pieceSize);
        }
        auto end = std::chrono::high_resolution_clock::now();
        auto time = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
        std::cout << time << ",";

        std::vector<unsigned char> rows(k);
        for (unsigned char i = 0; i < k; i++) {
            rows[i] = n - k + i;
        }
        for (unsigned char i = 0; i < k; i++) {
            memcpy(encoded.data() + i * pieceSize, src.data() + rows[i] * pieceSize, pieceSize);
        }
        start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < times; i++) {
            rsCode.decode(pieceSize, rows.data(), encoded.data(), decoded.data());
        }
        end = std::chrono::high_resolution_clock::now();
        time = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
        std::cout << time << std::endl;
    }

    void initialize(size_t _size) {
        size = _size;
        src.clear();
        encoded.clear();
        decoded.clear();
        src.resize(8 * (size + 256));
        encoded.resize(8 * (size + 256));
        decoded.resize(size + 256);
        for (size_t i = 0; i < size + 256; i++) {
            src[i] = rand() % 256;
        }
    }

    void testFileSize(size_t _size, size_t times) {
        initialize(_size);
        unsigned char n = 8;
        for (unsigned char k = 1; k <= n; k++) {
            testRSCode(n, k, times);
        }
        n = 128;
        for (unsigned char k = 8; k <= n; k+=8) {
            testRSCode(n, k, times);
        }
    }
};


int main() {
    Test test;

    std::cout << "size,n,k,times,encode,decode" << std::endl;
//    test.testFileSize(1024, 1000);
//    test.testFileSize(1024 * 1024, 10);
    test.testFileSize(1024 * 1024 * 1024, 1);

/*    RSCode rsCode(9, 6);

    size_t size = 100000000;

    auto *src = new unsigned char[9 * size];
    for (size_t i = 0; i < 6 * size; i++) {
        src[i] = rand() % 256;
    }
    auto parity = src + 6 * size;

    std::cout << "start encode" << std::endl;
    rsCode.encode(size, src, parity);
    std::cout << "end encode" << std::endl;

    unsigned char rows[] = {0, 1, 2, 3, 4, 5};
    auto *encoded = new unsigned char[6 * size];

    for (size_t i = 0; i < 6; i++) {
        memcpy(encoded + i * size, src + rows[i] * size, size);
    }

    auto *decoded = new unsigned char[6 * size];
    std::cout << "start decode" << std::endl;
    auto start = std::chrono::system_clock::now();

    rsCode.decode(size, rows, encoded, decoded);

    auto end = std::chrono::system_clock::now();
    auto time = std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count();
    std::cout << "time: " << time << "ms" << std::endl;
    std::cout << "end decode" << std::endl;

//    rsCode.decode(size, rows, encoded, decoded);
//    rsCode.decode(size, rows, encoded, decoded);
//    rsCode.decode(size, rows, encoded, decoded);
//    rsCode.decode(size, rows, encoded, decoded);
//    rsCode.decode(size, rows, encoded, decoded);


    for (size_t i = 0; i < 6 * size; i++) {
        if (src[i] != decoded[i]) {
            assert(false);
            exit(-1);
        }
    }*/


}
