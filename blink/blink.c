//***************************************************************************************
//  MSP430 Blink the LED Demo - Software Toggle P1.0
//
//  Description; Toggle P1.0 by xor'ing P1.0 inside of a software loop.
//  ACLK = n/a, MCLK = SMCLK = default DCO
//
//                MSP430x5xx
//             -----------------
//         /|\|              XIN|-
//          | |                 |
//          --|RST          XOUT|-
//            |                 |
//            |             P1.0|-->LED
//
//  Texas Instruments, Inc
//  July 2013
//***************************************************************************************

#include <msp430.h>

void main(void) {
    WDTCTL = WDTPW | WDTHOLD;               // Stop watchdog timer
    PM5CTL0 &= ~LOCKLPM5;                   // Disable the GPIO power-on default high-impedance mode
                                            // to activate previously configured port settings
    WDTCTL = WDTPW | WDTHOLD;                 // don't touch it, it's for the watchdog stuff

    P1DIR |= (BIT0 | BIT6);                   // set P1DIR with P0 and P6 to high (1)

    for (;;) {
        P1OUT ^= (BIT0 | BIT6);               // toggle the P0 and P6 of P1OUT with 1 and 0
        __delay_cycles(250000);               // 250000 microseconds between each cycle
    }
}
