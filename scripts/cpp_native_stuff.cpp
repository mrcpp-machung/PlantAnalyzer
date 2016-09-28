
//#include<iostream>
#include <stdint.h>
#include <stdio.h>
#include <math.h>
//using namespace std;

//calculates the square of the euclidiean difference in colors between pix1 and pix2
inline int colorDiff(uint8_t* pix1, uint8_t* pix2){
    int diff = 0;

    diff += (pix1[0]-pix2[0])*(pix1[0]-pix2[0]);
    diff += (pix1[1]-pix2[1])*(pix1[1]-pix2[1]);
    diff += (pix1[2]-pix2[2])*(pix1[2]-pix2[2]);

    return diff;
}

/*
    searches for pixels with unwanted colors in im and sets them to black (255,255,255).
    Parameters:
        - img: The image that shall be processed, width m, height n
        - unwanted colors: a list(!) with the unwanted colors specified as RGB values, length n
        - threshold: values between 0 and 3*256 make sense
*/
void cpp_colorMask(uint8_t* img, uint8_t* mask, int m, int n,
                     uint8_t* colors, int l, int threshold){
    threshold *= threshold;
    int i, j, k;

    for (i=0; i<n; i++){
        for (j=0; j<m; j++){
            mask[i*m+j] = 0;
        }
    }

    for (k=0; k<l; k++){
        for (i=0; i<n; i++){
            for (j=0; j<m; j++){
                if (colorDiff(&img[3*(i*m+j)], &colors[3*k]) < threshold){
                    mask[i*m+j] = 255;
                }
            }
        }
    }
    return ;
}


/*
    Equalizes the histogram of src and writes the result to dst.
    It doesn't check, whether we really have valid data!
    Parameters:
        -src: The source image wit data type float32
        -dst: The destination array with data type uint8
        - m,n: The dimensions of the arrays
*/
void cpp_RGHistogramEqualizer(float* src, uint8_t* dst, int m, int n){

    int i, j;
    float tmp;
    float  k = 0.05;

    for (i=0; i<n; i++){
        for (j=0; j<m; j++){

            if (src[i*m+j] <= 1.0){
                tmp = 128.0*src[i*m+j];
                tmp = round(255.0 /(1 + exp(-k*(tmp - 128))));
                dst[i*m+j] = (uint8_t) tmp;
            }

            else{
                tmp = 255.0 - 128.0/src[i*m+j];
                tmp = round(255.0 /(1 + exp(-k*(tmp - 128))));
                dst[i*m+j] = (uint8_t) tmp;
            }
        }
    }
    return ;
}
