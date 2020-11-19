//
// Created by liu on 18/11/2020.
//

#ifndef RSCODE_GF8_H
#define RSCODE_GF8_H

#include <ostream>
#include "LUT.h"

class GF8Matrix;

struct GF8 {
    unsigned char data = 0;

    GF8() = default;

    GF8(const GF8 &) = default;

    GF8(unsigned char data) : data(data) {};

    GF8 &operator=(const GF8 &) = default;

    GF8 &operator=(unsigned char _data) {
        data = _data;
        return *this;
    }

    GF8 operator+(const GF8 &that) const {
        return GF8(data ^ that.data);
    }

    GF8 &operator+=(const GF8 &that) {
        data ^= that.data;
        return *this;
    }

    GF8 operator-(const GF8 &that) const {
        return GF8(data ^ that.data);
    }

    GF8 &operator-=(const GF8 &that) {
        data ^= that.data;
        return *this;
    }

    GF8 operator*(const GF8 &that) const {
        return GF8(GF8_LUT_MUL[data][that.data]);
    }

    GF8 &operator*=(const GF8 &that) {
        data = GF8_LUT_MUL[data][that.data];
        return *this;
    }

    GF8 operator/(const GF8 &that) const {
        assert(data != 0);
        return GF8(GF8_LUT_DIV[data][that.data]);
    }

    GF8 &operator/=(const GF8 &that) {
        assert(data != 0);
        data = GF8_LUT_DIV[data][that.data];
        return *this;
    }
};

class GF8Matrix {
    GF8 *data;
    unsigned char rowSize;
    unsigned char colSize;

public:
    GF8Matrix(unsigned char rowSize, unsigned char colSize) : rowSize(rowSize), colSize(colSize) {
        data = new GF8[rowSize * colSize];
    }

    ~GF8Matrix() {
        delete[] data;
    }

    GF8 *operator[](size_t row) {
        assert(row < rowSize);
        return data + row * colSize;
    }

    const GF8 *operator[](size_t row) const {
        assert(row < rowSize);
        return data + row * colSize;
    }

    void copyRow(GF8Matrix &dest, size_t srcRow, size_t destRow) {
        assert(colSize == dest.colSize);
        for (unsigned char i = 0; i < colSize; i++) {
            dest[destRow][i] = (*this)[srcRow][i];
        }
    }

    void addRow(size_t srcRow, size_t destRow) {
        for (unsigned char i = 0; i < colSize; i++) {
            (*this)[destRow][i] += (*this)[srcRow][i];
        }
    }

    void multiAddRow(size_t srcRow, size_t destRow, GF8 multiplier) {
        for (unsigned char i = 0; i < colSize; i++) {
            (*this)[destRow][i] += (*this)[srcRow][i] * multiplier;
        }
    }

    void multiRow(size_t row, GF8 multiplier, size_t col = 0) {
        for (unsigned char i = col; i < colSize; i++) {
            (*this)[row][i] *= multiplier;
        }
    }

    int findRowLeader(unsigned char startRow, unsigned char col) {
        for (unsigned char i = startRow; i < colSize; i++) {
            if ((*this)[i][col].data != 0) {
                return i;
            }
        }
        return -1;
    }

    void partialLowerGaussElim(unsigned char &rowIndex, unsigned char &colIndex, GF8Matrix &result) {
        unsigned char lastRow = rowSize - 1;
        while (rowIndex < lastRow) {
            if (colIndex >= colSize) {
                return;
            }
            auto term = (*this)[rowIndex][colIndex];
            if (term.data == 0) {
                return;
            }
            auto divisor = GF8(1) / term;
            for (unsigned char k = rowIndex + 1; k < rowSize; k++) {
                auto nextTerm = (*this)[k][colIndex];
                if (nextTerm.data != 0) {
                    auto multiplier = divisor * (GF8(0) - nextTerm);
                    multiAddRow(rowIndex, k, multiplier);
                    result.multiAddRow(rowIndex, k, multiplier);
                }
            }
            rowIndex++;
            colIndex++;
        }
    }

    void lowerGaussianElim(GF8Matrix &result) {
        unsigned char rowIndex = 0, colIndex = 0;
        unsigned char lastRow = std::min<unsigned char>(rowSize - 1, colSize), lastCol = colSize - 1;
        while ((rowIndex < lastRow) && (colIndex < lastCol)) {
            int leader = findRowLeader(rowIndex, colIndex);
            if (leader < 0) {
                colIndex++;
                continue;
            }
            if (leader != rowIndex) {
                result.addRow(leader, rowIndex);
                addRow(leader, rowIndex);
            }
            partialLowerGaussElim(rowIndex, colIndex, result);
        }
    }

    void upperInverse(GF8Matrix &result) {
        auto lastCol = std::min<unsigned char>(rowSize, colSize);
        for (unsigned char colIndex = 0; colIndex < lastCol; colIndex++) {
            auto term = (*this)[colIndex][colIndex];
            assert(term.data != 0);
            auto divisor = GF8(1) / term;
            if (divisor.data != 1) {
                multiRow(colIndex, divisor, colIndex);
                result.multiRow(colIndex, divisor);
            }
            for (unsigned char rowToElim = 0; rowToElim < colIndex; rowToElim++) {
                auto nextTerm = (*this)[rowToElim][colIndex];
                auto multiplier = GF8(0) - nextTerm;
                multiAddRow(colIndex, rowToElim, multiplier);
                result.multiAddRow(colIndex, rowToElim, multiplier);
            }
        }
    }

    void inverse() {
        assert(rowSize == colSize);
        GF8Matrix result(colSize, colSize);
//        memset(result.data, 0, colSize * colSize * sizeof(GF8));
        for (unsigned char i = 0; i < colSize; i++) {
            result[i][i] = 1;
        }
        lowerGaussianElim(result);
        upperInverse(result);
        std::swap(data, result.data);
    }

    void transpose() {
        GF8Matrix result(colSize, rowSize);
        for (size_t i = 0; i < rowSize; i++) {
            for (size_t j = 0; j < colSize; j++) {
                result[j][i] = (*this)[i][j];
            }
        }
        std::swap(data, result.data);
        std::swap(colSize, rowSize);
    }

    friend std::ostream &operator<<(std::ostream &out, const GF8Matrix &matrix) {
        for (size_t i = 0; i < matrix.rowSize; i++) {
            for (size_t j = 0; j < matrix.colSize; j++) {
                out << (int) matrix[i][j].data << " ";
            }
            out << std::endl;
        }
        return out;
    }

    void multiplyColumn(GF8 *src, GF8 *dest, size_t startRow = 0) {
        for (unsigned char i = startRow; i < rowSize; i++) {
            GF8 result = 0;
            for (unsigned char j = 0; j < colSize; j++) {
                result += (*this)[i][j] * src[j];
            }
            dest[i - startRow] = result;
        }
    }

    void multiplyColumn(GF8 *src, GF8 *dest, unsigned char *rows) {
        for (unsigned char i = 0; i < rowSize; i++) {
            if (rows[i] > 0) continue;
            GF8 result = 0;
            for (unsigned char j = 0; j < colSize; j++) {
                result += (*this)[i][j] * src[j];
            }
            dest[i] = result;
        }
    }
};


#endif //RSCODE_GF8_H
