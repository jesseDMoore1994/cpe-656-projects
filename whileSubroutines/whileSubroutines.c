#include <stdio.h>
#include <msp430.h> 
#define ARR_SIZE 5

/**
 * whileSubroutines.c
 */
void blinkThreeTimes() {
    unsigned int x;
    for(x=6; x>0; x--) {
        volatile unsigned int i;            // volatile to prevent optimization

        P1OUT ^= 0x01;                      // Toggle P1.0 using exclusive-OR

        i = 10000;                          // SW Delay
        do i--;
        while(i != 0);
    }
    P1OUT = 0x00;
}

unsigned int scalarAdd(unsigned int x, unsigned int y) {
    return x + y;
}

void arrayAdd(unsigned int* a, unsigned int* b, unsigned int* result, unsigned int size) {
    unsigned int count;
    for(count=size-1; count<size; count--) {
        result[count] = a[count] + b[count];
    }
}

void performSubroutinesLoop() {
    unsigned int x = 0;
    unsigned int y = 0;

    unsigned int a[ARR_SIZE];
    unsigned int b[ARR_SIZE];
    unsigned int array_result[ARR_SIZE];

    unsigned int count;
    for(count=ARR_SIZE-1; count<ARR_SIZE; count--) {
        array_result[count] = 0;
        a[count] = 0;
        b[count] = 0;
    }

    do {
        volatile unsigned int scalar_result = scalarAdd(x, y);
        x = x > 9 ? 0 : x+1;
        y = y > 9 ? 0 : y+1;

        arrayAdd(a, b, array_result, ARR_SIZE);
        for(count=ARR_SIZE-1; count<ARR_SIZE; count--) {
            a[count] = a[count] > 9 ? 0 : a[count]+1;
            b[count] = b[count] > 9 ? 0 : b[count]+1;
        }
    } while(1);
}

int main(void) {
    WDTCTL = WDTPW | WDTHOLD;               // Stop watchdog timer
    PM5CTL0 &= ~LOCKLPM5;                   // Disable the GPIO power-on default high-impedance mode
                                            // to activate previously configured port settings
    P1DIR |= 0x01;                          // Set P1.0 to output direction

    blinkThreeTimes();
    performSubroutinesLoop();
    return 0;
}
