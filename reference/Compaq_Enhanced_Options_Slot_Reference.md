# Compaq Enhanced Options Slot — Reference

**Sources:** Compaq Portable 486c Reference Guide (P/N 128984-001, November 1991); Compaq LTE Lite guide (`8977986.pdf`, section 6.4)

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

## Sources for the Pinout

Two documents in this directory describe the slot:

- **486c Reference Guide** (`128984-001_...pdf`, Appendix D, pages D-4/D-5):
  pin numbers and short signal names only. No directions, polarities or
  descriptions. The scan's OCR also confuses Q/0 and D/O.
- **LTE Lite guide** (`8977986.pdf`, section 6.4, Table 6-3): the same 50
  pins with signal direction, polarity and function, plus the system-side
  configuration registers.

The pin numbers of the two tables match signal-for-signal, so this
reference treats them as the same interface. **That equivalence is an
inference and has not been verified on a Portable 486c.** Electrical
figures (350 mA, 2.5 us, 20 mA) are LTE Lite values.

---

## 50-Pin Connector Pinout

"Dir" is from the option card's point of view (In = driven by the system).
A trailing `-` means active low.

| Pin | 486c manual name | LTE Lite name | Dir | Function |
|-----|------------------|---------------|-----|----------|
| 1   | Ground           | GND           | —   | Ground |
| 2   | Data Bit <0>     | DB00          | I/O | Data bus, low byte |
| 3   | Data Bit <1>     | DB01          | I/O | |
| 4   | Data Bit <2>     | DB02          | I/O | |
| 5   | Data Bit <3>     | DB03          | I/O | |
| 6   | Data Bit <4>     | DB04          | I/O | |
| 7   | Data Bit <5>     | DB05          | I/O | |
| 8   | Data Bit <6>     | DB06          | I/O | |
| 9   | Data Bit <7>     | DB07          | I/O | |
| 10  | Select           | SLOT CS-      | In  | Low when the system's slot logic has decoded a valid I/O address |
| 11  | IOW              | SIOWC-        | In  | I/O write command |
| 12  | IOR              | SIORC-        | In  | I/O read command |
| 13  | IRQ              | SLOT IRQA     | Out | Interrupt request; system maps it to IRQ3 or IRQ4 |
| 14  | Bus Ready        | BUSRDY-       | Out | Pull low to lengthen the bus cycle (wait states). Open collector, 20 mA sink, max 2.5 us |
| 15  | +5V              | +5 VDC        | —   | Power, 350 mA total across pins 15 and 16 |
| 16  | +5V              | +5 VDC        | —   | |
| 17  | RST              | SLOT RST      | In  | Reset. Also pulsed for 10 ms when SLOT ON toggles |
| 18  | XA08             | SA0           | In  | Address bit 0 |
| 19  | Add 1            | SA1           | In  | Address bit 1 |
| 20  | Add 2            | SA2           | In  | Address bit 2 |
| 21  | Mclock           | COMMCLK       | In  | 1.8432 MHz UART clock, 50% duty. Stopped in standby |
| 22  | Reserve 1        | Reserved      | —   | Not used |
| 23  | Reserve 2        | WAKEUP-       | Out | Low brings the system out of standby (LTE Lite). Leave unconnected |
| 24  | Slot-on          | SLOT ON       | In  | System control for the card's low-power mode |
| 25  | SPKDRV           | MSPKDRV       | Out | Audio to system speaker (5 V RMS max into 10K) |
| 26  | Ground           | GND           | —   | Ground |
| 27  | Ground           | GND           | —   | Ground |
| 28  | DMA              | DMA           | In  | High while a DMA cycle is in progress |
| 29  | Data Bit <15>    | DB15          | I/O | Data bus, high byte (16-bit devices only) |
| 30  | Data Bit <14>    | DB14          | I/O | |
| 31  | Data Bit <13>    | DB13          | I/O | |
| 32  | Data Bit <12>    | DB12          | I/O | |
| 33  | Data Bit <11>    | DB11          | I/O | |
| 34  | Data Bit <10>    | DB10          | I/O | |
| 35  | Data Bit <9>     | DB09          | I/O | |
| 36  | Data Bit <8>     | DB08          | I/O | |
| 37  | Add 3            | SA3           | In  | Address bit 3 |
| 38  | Add 4            | SA4           | In  | Address bit 4 |
| 39  | Add 5            | SA5           | In  | Address bit 5 |
| 40  | Add 6            | SA6           | In  | Address bit 6 |
| 41  | Add 7            | SA7           | In  | Address bit 7 |
| 42  | Add 8            | SA8           | In  | Address bit 8 |
| 43  | Add 9            | SA9           | In  | Address bit 9 |
| 44  | SLOT-DMA-        | SLOT DMA-     | Out | Low tells the system the card can do DMA. Open collector, 20 mA |
| 45  | T-C              | T-C           | In  | High at DMA terminal count |
| 46  | SLOT-IRQB        | SLOT IRQB     | Out | Second interrupt, for programmable-address devices: IRQ3/4/5/7/9 |
| 47  | IO16             | I/O16-        | Out | Low tells the system the card supports 16-bit transfers. Open collector, 20 mA |
| 48  | SLOT-DRQ         | SLOT DRQ      | Out | DMA request (DRQ1, 3 or 5) |
| 49  | SLOT-IOEN        | SLOT IOEN-    | Out | Low indicates the card has a valid I/O address decode |
| 50  | SLOT-DAK         | SLOT DAK      | In  | DMA acknowledge |

### Notes on names

- **Pin 18 is address bit 0, not bit 8.** The 486c scan reads "XA08";
  the LTE Lite table lists pin 18 as SA0, and "Add 1"–"Add 9" are then
  A1–A9, giving the ten lines A0–A9.
- **Pin 46 is SLOT-IRQB, not "IR08"/IRQ8.** The 486c scan's OCR turns Q
  into 0 and B into 8. Likewise the scan shows "OMA", "SLOT-ORO",
  "SLOT-OAK" and "1016" for DMA, SLOT-DRQ, SLOT-DAK and IO16.
- **Pin 49 (SLOT IOEN-) is driven by the card**, not by the system. How
  the 486c uses it (most likely to enable its data buffers toward the
  slot) is not documented; confirm by measurement.

---

## System-Side Configuration (LTE Lite)

On the LTE Lite the slot's address decode and IRQ routing are set by
I/O-mapped registers, and the system generates SLOT CS-:

| Register | Address | Relevant function |
|----------|---------|-------------------|
| Peripheral Configuration | 0465h | COM1/COM2 decode select, decode enable, IRQA to IRQ3/IRQ4 |
| Option Slot Configuration | 2865h | Decode range length (8/16/32/64 bytes), IRQB and DMA mapping |
| Option Slot Address Decode | 2C65h | Programmable base address, enable bit 7 |
| Miscellaneous Options | 3465h | Bit 2 = SLOT ON |

Whether the Portable 486c has the same registers is unknown. Its manual
only describes assigning COM1/COM2 resources through the EISA
Configuration Utility and setting jumpers on the card, which leaves open
whether the 486c pre-decodes SLOT CS- or expects the card to decode
A3–A9 itself.

---

## Bus Characteristics

- Subset of the ISA bus; the LTE Lite guide states signal timing is
  identical to ISA
- 16-bit data bus, 10 address lines (A0–A9)
- Two interrupt outputs (IRQA, IRQB)
- Wait-state support via BUSRDY-
- DMA support via DMA, SLOT DMA-, SLOT DRQ, SLOT DAK, T-C
- +5V only, 350 mA (LTE Lite figure); no ±12V
- UART clock (1.8432 MHz) supplied on pin 21

---

## Original Compaq Modem (from photos of the board)

Compaq internal modem, spare no. 125925-001, assembly 002160-001, bare
board 002162-001, copyright 1991/1992, FCC ID CNT75M87Z.

Probably the "Enhanced 9600-bps Data+Fax Modem", option part 125901-002
in the LTE Lite guide's options list (the board's own numbers are all in
the same 1259xx range; the match is by number range, not confirmed).

No datasheet, schematic or technical reference for this modem was found
online (searched November 2026 by spare number, label number, FCC ID and
product name). The LTE Lite guide's diagnostics table (error codes
1201-xx) tests the modem as a standard UART: DLAB bit, THRE, Data Ready,
TX/RX buffer, interrupt on COM1/COM2, and control signals.

| Ref | Marking | Identification |
|-----|---------|----------------|
| U501 | Compaq 125905-003 (1992, QFP) | Custom ASIC beside the 50-pin connector; presumed host bus interface |
| U3 | Large QFP, marking hidden by a barcode label | Presumed controller CPU |
| U1 | Intel N27C220-150V10, Compaq 125934-002, socketed PLCC | 2 Mbit 16-bit-wide EPROM (firmware) |
| U505, U506 | M5M5256BVP-10LL x2 | 32K x 8 SRAM |
| — | X24C16S | 16 Kbit serial EEPROM (stored settings) |
| U2 | AT&T WE DSP16A | DSP (data pump) |
| U500 | AT&T M-V.32-INTFC-F | V.32 interface chip |
| U4 | AT&T T7525 | Codec |
| U503 | 70M376-CH | Analog line-interface part (not positively identified) |
| — | 16.000 MHz and 40.550 MHz oscillators | No 1.8432 MHz source on the card |
| — | Transformer, relay, LH1516, LM358 | Phone line interface |

Observations relevant to a replacement card:

- There is no discrete 16450/16550. The UART register interface is
  implemented in the ASIC.
- No buffer or transceiver chips sit between the connector and the ASIC.
- No jumpers or DIP switches, so the COM port is not selected on the card.
- Bulk capacitance on the 5V rail is three 68 uF tantalums.
- Two 50-pin connector positions carry the slot signals: J1 (right-angle
  receptacle on a short edge) and J4 (two rows of 25 through-holes along
  a long edge).
- Silkscreen marks pins 1 and 2 side by side at one end of J4 and 49 and
  50 at the other, and pin 2 and pin 50 at opposite ends of J1. Numbering
  is therefore odd/even across the rows, not one row 1-25 and the other
  26-50.

---

## Photos

In `photos/`:

| File | Shows |
|------|-------|
| `slot-j22-system-io-board.jpg` | The slot header (J22) on the 486c System I/O board, with the Torx standoff beside it |
| `slot-j22-closeup.jpg` | J22 from above: shrouded 2x25 male header |
| `modem-connector-edge-on.jpg` | Original modem seen edge-on, looking into the 2x25 receptacle |
| `modem-top-both-connectors.jpg` | Modem top side with both 50-pin connectors (J1 and J4) still fitted |
| `modem-top-j4-removed.jpg` | Modem top side after J4 was desoldered; J1/J4 pin-number silkscreen visible |
| `modem-top-j4-removed-rotated.jpg` | Same, rotated 180 degrees |
| `modem-bottom.jpg` | Modem bottom side: host-interface ASIC (U501), V.32 interface chip, SRAMs, EEPROM |

---

## System Context

The Compaq Portable 486c (33 MHz i486 with integrated FPU and 8 KB cache) also featured:

- Two full-sized internal EISA expansion slots (for more complex boards)
- Standard integrated interfaces: Parallel, Serial, Mouse, External Keyboard, External VGA Display, External Storage, CD-ROM, Audio In
- The Enhanced Options Slot is physically located on the I/O board and accessed from the rear of the unit

---

*Pin names from the Compaq Portable 486c Reference Guide (P/N 128984-001, November 1991). Directions, functions and configuration registers from the Compaq LTE Lite guide (`8977986.pdf`, section 6.4).*
