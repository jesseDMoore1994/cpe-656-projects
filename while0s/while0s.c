#include <stdio.h>
#include <msp430.h> 


/**
 * while0s.c
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

void performZerosLoop() {
    volatile unsigned int guard, x, y, z;
    guard = 0; x = 0; y = 0; z = 0;
    do {
        x = y + z;
        y = z - x;
        z = x * y;
    } while(guard == 0);
}

int main(void) {
    WDTCTL = WDTPW | WDTHOLD;               // Stop watchdog timer
    PM5CTL0 &= ~LOCKLPM5;                   // Disable the GPIO power-on default high-impedance mode
                                            // to activate previously configured port settings
    P1DIR |= 0x01;                          // Set P1.0 to output direction
	
    blinkThreeTimes();
    performZerosLoop();
	return 0;
}
