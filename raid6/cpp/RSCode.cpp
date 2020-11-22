//
// Created by liu on 18/11/2020.
//

#include <cstring>
#include <iostream>
#include "RSCode.h"

RSCode::RSCode(unsigned char n, unsigned char k) :
        n(n), k(k), encoder(n, k), decoder(k, k) {
    assert(n > 0);
    assert(n >= k);
    tempData = new GF8[2 * n];
    rowFlags = new unsigned char[k];
    for (unsigned char i = 0; i < n; i++) {
        GF8 term = 1;
        for (unsigned char j = 0; j < k; j++) {
            encoder[i][j] = term;
            term *= i;
        }
    }
    auto temp = GF8Matrix(n, k);
    encoder.transpose();
    encoder.lowerGaussianElim(temp);
    encoder.upperInverse(temp);
    encoder.transpose();
//    std::cout << encoder << std::endl;
}

RSCode::~RSCode() {
    delete[] tempData;
    delete[] rowFlags;
}

void RSCode::encode(size_t size, unsigned char *raw, unsigned char *parity) {
    if (n == k) return;
    for (size_t i = 0; i < size; i++) {
        for (unsigned char j = 0; j < k; j++) {
            tempData[j] = raw[size * j + i];
        }
        encoder.multiplyColumn(tempData, tempData + k, k);
        for (unsigned char j = 0; j < n - k; j++) {
            parity[size * j + i] = tempData[k + j].data;
        }
    }
}

void RSCode::decode(size_t size, unsigned char *rows, unsigned char *encoded, unsigned char *decoded) {
    memset(rowFlags, 0, k);
    unsigned char deletedRowSize = 0;
    for (unsigned char i = 0; i < k; i++) {
        assert(rows[i] < n);
        encoder.copyRow(decoder, rows[i], i);
        if (rows[i] < k) {
            rowFlags[rows[i]] = 1;
            memcpy(decoded + rows[i] * size, encoded + i * size, size);
        } else {
            deletedRowSize++;
        }
    }
    if (n == k) return;
    decoder.inverse();
    for (size_t i = 0; i < size; i++) {
        for (unsigned char j = 0; j < k; j++) {
            tempData[j] = encoded[size * j + i];
        }
        decoder.multiplyColumn(tempData, tempData + k, rowFlags);
        for (unsigned char j = 0; j < k; j++) {
            if (rowFlags[j] == 0) {
                decoded[size * j + i] = tempData[k + j].data;
            }
        }
    }
//    std::cout << decoder << std::endl;
}
