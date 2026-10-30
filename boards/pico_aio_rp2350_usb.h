/*
 * Board definition for the RP2350 USB board with WS2812 on GPIO22.
 */

#ifndef _BOARDS_PICO_AIO_RP2350_USB_H
#define _BOARDS_PICO_AIO_RP2350_USB_H

#include "boards/pico2.h"

#ifndef PICO_DEFAULT_WS2812_PIN
#define PICO_DEFAULT_WS2812_PIN 22
#endif

#define PICO_AIO_FORCE_WS2812 1

#endif
