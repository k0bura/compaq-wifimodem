# Compaq Enhanced Options Slot — Reference

**Source:** Compaq Portable 486c Reference Guide (P/N 128984-001, November 1991)

---

## Overview

The Enhanced Options Slot is a proprietary 50-pin expansion connector found in the COMPAQ Portable 486c Personal Computer. It is designed to accept a modem or a second serial interface board. It is separate from the two full-sized internal EISA expansion slots also present in the system.

---

## Intended Use

- Internal modem installation
- Second serial interface board
- Other compatible enhanced option cards

The slot connects to the system's I/O board. Options installed in this slot slide in from the rear of the computer and engage the 50-pin connector. An Enhanced Option Shield (included with the computer) is mounted on the back of the option board for EMI shielding and structural support, secured with Torx T-8 and T-15 screws.

---

## Installation Notes (from Chapter 3)

1. Power off and disconnect AC power.
2. Remove rear panel and options cover.
3. Push out metal clip(s) on the options cover that align with the options door.
4. Remove boards from EISA option slots 1 and 2 (for access).
5. Unplug fan power cable and remove fan screw (Torx T-15).
6. Place the Enhanced Option Shield on the back of the modem/option board, aligning holes.
7. Secure with two Torx T-8 screws.
8. Slide the option board in from the back, pressing down gently until connectors engage.
9. Reinsert the Torx T-15 screw through the Enhanced Option Shield tab to the I/O board.
10. Reassemble in reverse order.

**CAUTION:** Handle the option board carefully — some components are fragile. The board must be securely connected to operate properly.

---

## Configuration

Options installed in the Enhanced Options Slot may need to be configured using the **COMPAQ EISA Configuration Utility**. Two methods are available:

- **Method 1 (Manual):** If no configuration (.CFG) file exists for the board, manually set switches/jumpers on the board based on available system resources (IRQ, port addresses) shown in the utility.
- **Method 2 (Generic Config File):** Use a generic ISA adapter definition in the EISA Configuration Utility, then manually edit port address and IRQ resources and lock the board.

**Example:** A modem configured at COM1 requires IRQ4 and port addresses 3F8–3FF. COM2 requires IRQ3 and port addresses 2F8–2FF. The EISA Configuration Utility can reallocate resources if conflicts arise.

---

## 50-Pin Connector Pinout

### Pins 1–40

| Pin | Signal         | Pin | Signal         |
|-----|----------------|-----|----------------|
| 1   | Ground         | 21  | Mclock         |
| 2   | Data Bit <0>   | 22  | Reserve 1      |
| 3   | Data Bit <1>   | 23  | Reserve 2      |
| 4   | Data Bit <2>   | 24  | Slot-on        |
| 5   | Data Bit <3>   | 25  | SPKDRV         |
| 6   | Data Bit <4>   | 26  | Ground         |
| 7   | Data Bit <5>   | 27  | Ground         |
| 8   | Data Bit <6>   | 28  | DMA            |
| 9   | Data Bit <7>   | 29  | Data Bit <15>  |
| 10  | Select         | 30  | Data Bit <14>  |
| 11  | IOW            | 31  | Data Bit <13>  |
| 12  | IOR            | 32  | Data Bit <12>  |
| 13  | IRQ            | 33  | Data Bit <11>  |
| 14  | Bus Ready      | 34  | Data Bit <10>  |
| 15  | +5V            | 35  | Data Bit <9>   |
| 16  | +5V            | 36  | Data Bit <8>   |
| 17  | RST            | 37  | Add 3          |
| 18  | XA08           | 38  | Add 4          |
| 19  | Add 1          | 39  | Add 5          |
| 20  | Add 2          | 40  | Add 6          |

### Pins 41–50

| Pin | Signal       |
|-----|--------------|
| 41  | Add 7        |
| 42  | Add 8        |
| 43  | Add 9        |
| 44  | SLOT-DMA-    |
| 45  | T-C          |
| 46  | SLOT-IR08    |
| 47  | IO16         |
| 48  | SLOT-DRQ     |
| 49  | SLOT-IOEN    |
| 50  | SLOT-DAK     |

---

## Signal Descriptions

### Data Bus
- **Data Bit <0> – <15>** (Pins 2–9, 29–36): 16-bit data bus, supporting ISA-style 16-bit transfers.

### Address Bus
- **XA08** (Pin 18): Address line 8
- **Add 1 – Add 9** (Pins 19–20, 37–43): Address lines for I/O port decoding (10 address lines total including XA08, providing up to 1024 I/O port addresses).

### Control Signals
- **IOW** (Pin 11): I/O Write — active when the CPU is writing to an I/O port.
- **IOR** (Pin 12): I/O Read — active when the CPU is reading from an I/O port.
- **IRQ** (Pin 13): Interrupt Request — directly from the option board to the system interrupt controller.
- **Bus Ready** (Pin 14): Indicates the device is ready / used for wait-state insertion.
- **RST** (Pin 17): System Reset.
- **Select** (Pin 10): Chip select / board select signal.
- **IO16** (Pin 47): Indicates the device supports 16-bit I/O transfers.
- **SLOT-IOEN** (Pin 49): Slot I/O Enable — enables the slot for I/O access.

### DMA Signals
- **DMA** (Pin 28): DMA signal.
- **SLOT-DMA-** (Pin 44): Slot DMA request (active low).
- **SLOT-DRQ** (Pin 48): Slot DMA Request.
- **SLOT-DAK** (Pin 50): Slot DMA Acknowledge.
- **T-C** (Pin 45): Terminal Count — signals end of a DMA transfer.

### Power and Ground
- **+5V** (Pins 15, 16): +5V DC power supply.
- **Ground** (Pins 1, 26, 27): Ground/return.

### Miscellaneous
- **Mclock** (Pin 21): Master clock signal.
- **Slot-on** (Pin 24): Indicates the slot is active/populated.
- **SPKDRV** (Pin 25): Speaker drive — allows the option board to drive the system speaker (e.g., modem audio).
- **Reserve 1** (Pin 22): Reserved for future use.
- **Reserve 2** (Pin 23): Reserved for future use.
- **SLOT-IR08** (Pin 46): Secondary interrupt (IRQ8 line, from the second PIC).

---

## Bus Characteristics

The Enhanced Options Slot is essentially a simplified, proprietary ISA-like bus with the following characteristics:

- **16-bit data bus** (Data Bit <0> through <15>)
- **10 address lines** (XA08, Add 1–9) — sufficient for standard ISA I/O port decoding
- **Single IRQ line** plus a secondary interrupt (SLOT-IR08)
- **DMA support** via DMA, SLOT-DMA-, SLOT-DRQ, SLOT-DAK, and T-C signals
- **+5V power only** (no ±12V lines)
- **50-pin form factor** — much smaller than a standard ISA slot

This makes it well-suited for simple peripherals like modems and serial ports that need only I/O port access, one interrupt, and optionally DMA, without requiring the full ISA/EISA bus.

---

## System Context

The Compaq Portable 486c (33 MHz i486 with integrated FPU and 8 KB cache) also featured:

- Two full-sized internal EISA expansion slots (for more complex boards)
- Standard integrated interfaces: Parallel, Serial, Mouse, External Keyboard, External VGA Display, External Storage, CD-ROM, Audio In
- The Enhanced Options Slot is physically located on the I/O board and accessed from the rear of the unit

---

*Extracted from Compaq Portable 486c Reference Guide, Part Number 128984-001, November 1991. Available at bitsavers.org.*
