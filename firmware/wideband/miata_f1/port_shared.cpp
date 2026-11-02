#include "port_shared.h"

static const CANConfig canConfig500 =
{
    CAN_MCR_ABOM | CAN_MCR_AWUM | CAN_MCR_TXFP,
    /*
     APB1 = 24 MHz: pre-scaler 3, seg 1 = 13, seg 2 = 2 (16 tq, sample point 87.5 %). Subtract 1 for the registers.
    */
    CAN_BTR_SJW(0) | CAN_BTR_BRP(2)  | CAN_BTR_TS1(12) | CAN_BTR_TS2(1),
};

const CANConfig& GetCanConfig() {
    return canConfig500;
}
