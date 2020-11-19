//
// Created by liu on 18/11/2020.
//

#ifndef RSCODE_RSCODE_H
#define RSCODE_RSCODE_H

#include <cassert>
#include "GF8.h"

class RSCode {
private:
    unsigned char n;
    unsigned char k;
    GF8Matrix encoder;
    GF8Matrix decoder;
    GF8 *tempData;
    unsigned char *rowFlags;

public:
    RSCode(unsigned char n, unsigned char k);

    ~RSCode();

    void encode(size_t size, unsigned char *raw, unsigned char *parity);

    void decode(size_t size, unsigned char *rows, unsigned char *encoded, unsigned char *decoded);
};


#endif //RSCODE_RSCODE_H
