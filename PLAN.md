# ESP32 WiFi Modem for Compaq Enhanced Options Slot

## Goal

A Hayes-compatible WiFi modem card for the Compaq Portable 486c's 50-pin
Enhanced Options Slot, bridging AT commands to WiFi/TCP connections.

## Architecture

```
486c slot (5V, ISA timing) <--> 16C550 UART <--serial, TTL--> ESP32 <--> WiFi
```

A real 16C550 UART sits on the bus and the ESP32 sits on its serial side,
in the place a modem data pump would occupy. The UART handles all bus
timing, register behaviour, FIFOs and interrupts in hardware, so the ESP32
firmware is an ordinary serial-to-WiFi modem with no real-time bus work.

This replaces the earlier plan of having the ESP32 emulate the 16550
registers directly on the bus. See "Alternative Not Chosen" for why.

---

### How this compares with the original Compaq modem

The original card (Compaq 9600 bps modem, spare 125925-001) has the same
partition:

| Original | This design |
|----------|-------------|
| Compaq host-interface ASIC (125905-003) next to the connector | 16C550 |
| Controller CPU + 27C220 firmware EPROM + 2x 32K SRAM + EEPROM | ESP32 (flash, RAM, NVS) |
| AT&T DSP16A data pump, codec, line interface | ESP32 WiFi |

The original keeps the bus interface in dedicated hardware and the modem
logic in a separate processor behind it, with no buffers between the
connector and the ASIC and no jumpers for COM port selection. It has no
discrete UART; the ASIC presents the UART registers itself. See the
reference file for the component list.

---

## Sources and Confidence

The 486c manual (Appendix D) gives only pin numbers and terse signal names.
Signal directions, polarities and functions in this plan come from the
LTE Lite guide (`reference/8977986.pdf`, section 6.4), which documents a
50-pin enhanced option slot whose pin numbers match the 486c's
signal-for-signal.

**Assumption:** the two slots are the same interface. This is an inference
from the matching pinouts and is not yet confirmed on the 486c. Phase 0a
exists to confirm it before anything drives the bus.

See `reference/Compaq_Enhanced_Options_Slot_Reference.md` for the full pin
table.

---

## Bus Summary

Directions are from the card's point of view.

| What | Pins | Dir | Details |
|------|------|-----|---------|
| Data bus | 2-9 (D0-D7) | I/O | 8 bits is all a UART needs. D8-D15 (29-36) unused. |
| Address | 18 (A0), 19 (A1), 20 (A2) | In | Register select. Pin 18 is A0, "Add 1" is A1, "Add 2" is A2. |
| Upper address | 37-43 (A3-A9) | In | Only needed if SLOT CS- turns out not to be pre-decoded. |
| SLOT CS- ("Select") | 10 | In | Active low. On the LTE Lite the system pre-decodes this as COM1/COM2. |
| IOR-, IOW- | 12, 11 | In | Active low, ISA timing. |
| SLOT IOEN- | 49 | **Out** | Active low. Card tells the system it has a valid address decode. The original modem leaves it unconnected. |
| SLOT IRQA ("IRQ") | 13 | Out | System maps it to IRQ3 or IRQ4. |
| SLOT RST | 17 | In | Reset. Presumed active high (as ISA RESET DRV); verify. |
| COMMCLK ("Mclock") | 21 | In | 1.8432 MHz UART clock (LTE Lite). The 486c System I/O board has a 1.8432 MHz oscillator (Y2), so the clock is likely present; verify on pin 21. |
| DMA | 28 | In | High during DMA cycles (acts as ISA AEN). Only needed for own decode. |
| +5V | 15, 16 | — | 350 mA total (LTE Lite figure). |
| GND | 1, 26, 27 | — | Only three grounds. Keep wiring short. |

Not used: BUSRDY- (14; the 16550 is fast enough without wait states),
WAKEUP- (23, leave unconnected), SLOT ON (24), remaining DMA signals,
SLOT IRQB (46), I/O16- (47). MSPKDRV (25) is optional, see Phase 4.

---

## Hardware Design

### UART

16C550 powered at 5V, so the bus side needs no level shifting.
The part is the TL16C550CFN (PLCC-44), for both breadboarding and the
final card. The DIP-40 version (TL16C550CN) is obsolete.

For breadboarding the chip sits in a "PLCC44-DIP40 V2.0" programmer
adapter (on hand), which has two jumpers marked "flash" and "51". Set
both to "51". The wiring the 16550 needs leaves out PLCC pins 1, 12, 23
and 34, which are unconnected on the chip:

| DIP-40 pin | PLCC-44 pin |
|------------|-------------|
| 1-10 | 2-11 |
| 11-20 | 13-22 |
| 21-30 | 24-33 |
| 31-40 | 35-44 |

With that wiring the adapter's DIP pins follow the standard DIP-40 16550
pinout. **Not yet verified on the adapter:** check all 40 pins for
continuity against this table with the socket empty, and check the table
itself against the datasheet's N and FN pin diagrams, before fitting a
chip. Power and ground are DIP 40 and DIP 20.

| 16550 pin | Connects to | Notes |
|-----------|-------------|-------|
| D0-D7 | Slot 2-9 | Direct |
| A0, A1, A2 | Slot 18, 19, 20 | |
| CS2- | Slot 10 (SLOT CS-) | If pre-decoded. Otherwise from own decoder (below) |
| CS0, CS1 | +5V | |
| RD- | Slot 12 (IOR-) | |
| WR- | Slot 11 (IOW-) | |
| RD, WR, ADS- | GND | Unused alternate-polarity strobes |
| MR | Slot 17 (SLOT RST) | MR is active high; invert if Phase 0a shows RST is active low |
| XIN | Slot 21 (COMMCLK) | XOUT open. Fallback: 1.8432 MHz oscillator on the card |
| BAUDOUT- | RCLK | Also to the ESP32 for baud tracking (level shifted) |
| INTRPT | Slot 13 via 74HCT125 | Buffer enabled by OUT2-, the PC convention |
| OUT2- | 74HCT125 enable | |
| SOUT, RTS-, DTR- | ESP32 inputs | 5V outputs, must be level shifted down |
| SIN, CTS-, DSR-, DCD-, RI- | ESP32 outputs | 3.3V drive meets the 16550's TTL input thresholds directly |

### Glue logic

- Parts: SN74HCT125N (DIP-14); the SN74AHCT125N is an equivalent
  substitute. Tie unused buffer inputs to ground and their enables to +5V.
- **IRQ gate:** one 74HCT125 section, input INTRPT, enable OUT2-, output to pin 13.
- **IOEN-:** leave slot pin 49 unconnected, copying the original modem
  (see "Tracing results"). Fallback if reads return `FF`: a 74HCT125
  section driving pin 49 low while SLOT CS- is low.
- **Own address decode (not expected to be needed; the original modem
  has none, see "Tracing results"):**
  compare A3-A9 against 0x2F8 with pin 28 (DMA) low, using a 74HCT688
  (CD74HCT688E, DIP-20) or a GAL, and feed the result to CS2- and IOEN-.
- **Reset inverter (only if SLOT RST is active low):** one section of an
  SN74HCT04N. Use the HCT part, not HC, for TTL input thresholds.

### ESP32 side

All 5V-to-ESP32 signals go through an SN74LVC245AN (DIP-20, on hand)
powered at **3.3V** (5V-tolerant inputs, 3.3V outputs). ESP32 GPIOs are
not 5V tolerant. Do not use 74HCT parts powered at 5V for this direction.
A 74LVC125 or 74LVC244 would do the same job.

| 74LVC245A pin | Connects to |
|---------------|-------------|
| 20 (VCC) | 3.3V from the ESP32 board, 100 nF to ground |
| 10 (GND) | Ground |
| 1 (DIR) | 3.3V (direction A to B) |
| 19 (OE-) | Ground (always enabled) |
| 2-5 (A1-A4) | 16550 SOUT, RTS-, DTR-, BAUDOUT- |
| 18-15 (B1-B4) | The matching ESP32 inputs |
| 6-9 (A5-A8) | Ground (unused) |
| 14-11 (B5-B8) | Unconnected |

Check the pin numbers against the datasheet before powering up.

| Signal | ESP32 | Direction | Level shift |
|--------|-------|-----------|-------------|
| SOUT | UART RX | In | 74LVC |
| SIN | UART TX | Out | None |
| RTS- | UART CTS | In | 74LVC |
| CTS- | UART RTS | Out | None |
| DTR- | GPIO | In | 74LVC |
| DCD- | GPIO | Out | None |
| RI- | GPIO | Out | None |
| BAUDOUT- | GPIO (pulse counter) | In | 74LVC |

| OLED SDA | GPIO (I2C) | In/out | None (3.3V bus) |
| OLED SCL | GPIO (I2C) | Out | None (3.3V bus) |

DSR- is tied low (modem always ready). Total: 10 GPIOs, 8 for the UART
side and 2 for the status display. Use a UART other than UART0 so the
USB console stays free for debugging.

The serial side is TTL-level and non-inverted (idle high, modem-control
lines active low), which matches the ESP32 UART directly. No RS-232
transceiver is involved.

### Baud rate tracking

DOS software sets the baud rate by programming the 16550's divisor, which
the ESP32 cannot see. BAUDOUT- outputs 16x the programmed baud rate, so
the ESP32 measures its frequency with the pulse counter and sets its own
UART to match. Maximum is 115200 with the 1.8432 MHz clock (BAUDOUT- at
1.8432 MHz).

Early phases can skip this and use a fixed rate on both sides.

### Rear panel: antenna and status display

The case has an opening for the original modem's two phone jacks. The
card reuses it for an external WiFi antenna and a connector for an
external status display. The opening's dimensions and its position
relative to the card have not been measured yet; measure both before
designing the plate or choosing a pigtail length.

**Antenna**

- Use an ESP32 module with a U.FL (IPEX) antenna connector instead of a
  PCB antenna: ESP32-WROOM-32U, or the DevKitC-32U dev board. A PCB
  antenna inside the case would sit behind the machine's shielding.
- A short U.FL to RP-SMA bulkhead pigtail carries the signal to the
  opening. A standard 2.4 GHz RP-SMA antenna screws on from outside.
- A bulkhead RP-SMA needs a round hole of about 6.5 mm. A small plate
  (3D-printed or sheet metal) covers the phone-jack opening and holds the
  connector. Fix the plate to the card so the assembly slides in as one
  piece, as the original modem did.
- The plate must take the antenna's leverage. The U.FL socket takes no
  strain and is rated for only a few dozen matings.
- With a metal plate the connector shell joins card ground to chassis
  ground at that point. Check it with a multimeter so it is a known
  connection.
- Not chosen: an edge-mount SMA soldered to the card. It needs a 50-ohm
  trace from the module to the connector, for no gain over the pigtail.

**Status display**

- SSD1306 I2C OLED module (0.96" or 1.3", 128x64), in a small external
  enclosure on a cable up to about 1 m, I2C at 100 kHz.
- Shows SSID, signal strength, IP address, connection state (idle,
  dialling, connected and to where) and the current baud rate.
- Connector in the second jack position: 6-pin RJ12.

  | RJ12 pin | Signal |
  |----------|--------|
  | 1 | 3.3V |
  | 2 | GND |
  | 3 | SDA |
  | 4 | SCL |
  | 5, 6 | Spare (button or LED) |

- 3.3V comes from the ESP32 board's regulator. The display draws about
  20 mA, which counts against the slot's 350 mA.
- The lines leave the case, so each gets a series resistor (100 ohm) and
  an ESD protection diode. I2C pull-ups (4.7K to 3.3V) go on the card.
- **A phone line must never be plugged into this jack**; ring voltage
  (about 90 V AC) would destroy the card. Label the jack. If that is not
  safe enough, use a connector that cannot be mistaken for a phone jack
  (3.5 mm 4-pole or mini-DIN) on the same plate as the antenna.
- The firmware must run normally with no display attached.
- USB was considered for this and rejected: the ESP32 has no native USB,
  and connecting the dev board's USB while slot-powered backfeeds the
  Compaq's 5V rail (see Power).

### Power

- ESP32 dev board's 5V/VIN pin fed from slot pins 15/16.
- Add bulk capacitance (470 uF or more) near the ESP32 and reduce WiFi TX
  power; transmit bursts can exceed the 350 mA budget.
- **Never connect USB to the dev board while it is powered from the slot**
  (backfeeds the Compaq's 5V rail). Flash it out of the machine, or cut
  the USB 5V line on the debug cable.

### Physical connection

- System side (J22 on the System I/O board): shrouded 2x25 male pin
  header, 1.27 mm pitch, pins pointing up. The shroud is keyed, so
  generic 1.27 mm sockets and off-the-shelf pitch adapters do not fit.
  The breakout must carry the original receptacle.
- Card side: 2x25 female receptacle, 1.27 mm pitch, mounted at the card's
  bottom edge. One has been desoldered from an original modem and is on hand.
- **Pin numbering is odd/even across the two rows** (1 and 2 side by side
  at one end, 49 and 50 at the other), per the silkscreen on the original
  modem at both connector positions (J1 and J4). Confirm that this matches
  the manual's pin numbers by checking that pads 1, 26 and 27 are ground
  and 15 and 16 are joined, on the modem PCB with a multimeter.
- The original modem has two 50-pin connector positions: J1 (on the short
  edge opposite the phone jacks, still fitted) and J4 (along a long edge,
  desoldered, receptacle on hand). **J4 is the one the 486c uses**: the
  modem stands upright on its long edge, perpendicular to the System I/O
  board, with the phone jacks facing the rear of the machine. J4's
  receptacle is right-angle, opening downward along the board plane.
- A replacement card or breakout therefore also stands upright on J22 and
  should stay within the modem's outline.
- **Receptacle footprint:** 2 x 25 through-hole on a plain 1.27 mm x
  1.27 mm grid (no stagger). Established by fit: the bare receptacle
  seats in a Proto-Advantage SBBTH127P board (1.27 mm grid, 0.64 mm
  plated holes, 1.0 mm pads). Use 0.65 mm finished holes and 1.0 mm pads.
- **Mounting side and numbering:** on the modem the receptacle body is
  on the bottom side and the J4 silkscreen is on the top side. Seen from
  the top side, odd pins are the row farther from the board edge and
  even pins the row nearer the edge. Copy this arrangement exactly and
  the numbering comes out right.
- **Edge distance:** 2.55 mm (in effect 0.1") from the board edge to the
  centre of the J4 hole row nearest the edge, measured on the modem. The
  second row is then 3.82 mm from the edge. This sets the receptacle's
  overhang; holes farther in would let the board edge hit J22's shroud
  before the contacts engage.
- **Breakout board (Phase 0a/0b):** designed in `hardware/eos-breakout/`,
  generated by `gen_breakout.py`, and on order from OSH Park. 69.7 x
  31.9 mm, four layers, no vias: the original receptacle on the bottom
  edge fanned out to a labelled 2x25 0.1" header. The even-pin traces
  escape through the 2 mm strip between the pads and the board edge,
  spread over all four layers (0.16 mm traces, 0.20 mm gaps, more than
  15 mil from the edge), within OSH Park's 4-layer rules. Passes KiCad
  DRC. The 1:1 paper print has been checked against the modem's J4 holes
  and matches. Twelve of the even-pin traces run on the two inner
  layers, so when the boards arrive check continuity from every header
  pin to its slot pad before soldering the receptacle.
- For Phase 0b, short wires (under 10 cm) from the header to the 16550,
  in its PLCC-to-DIP adapter on a breadboard, are acceptable for a first
  test.
- Final: custom card PCB with the receptacle on the bottom edge, the 16550
  and glue logic beside it, the ESP32 module above, and a mounting point
  for the Torx standoff next to J22.

---

## Phase 0a: Passive Bus Sniffing

**Goal:** Learn what the 486c actually does on the slot before driving anything.

Nothing connected to the slot may drive a signal in this phase.

1. Establish pin numbering and verify +5V and GND with a multimeter.
2. Configure COM2 (0x2F8, IRQ3) for the slot in the EISA Configuration Utility.
3. Attach a logic analyzer (8 channels, 24 MHz is enough) to SLOT CS-,
   IOR-, IOW-, A0-A2, RST and pin 21.
4. In `DEBUG`, run `I 2F8`, `I 2F9`, `O 2F8 55`, and `I 3F8` as a control.
5. Capture a power-on or reset.

Questions to answer:

- Does SLOT CS- pulse low only for 2F8-2FF? (pre-decoded) Or never? (card must decode)
- Does pin 18 toggle as A0 between `I 2F8` and `I 2F9`?
- Is there a 1.8432 MHz clock on pin 21?
- Is RST active high?

### Tracing the original modem (no PC needed)

The modem's J4 pads are exposed, and its host-interface ASIC (U501,
Compaq 125905-003) sits right behind the connector. With a multimeter in
continuity mode, check which J4 pads reach U501:

- Pin 10 (SLOT CS-) connected, pins 37-43 (A3-A9) not -> the modem relies
  on the system's pre-decode, and so can this design.
- Pins 37-43 connected -> the modem decodes addresses itself; plan for
  the 74HCT688/GAL decoder.
- Pin 21 (COMMCLK) connected to anything -> the clock is expected to be there.
- Pin 49 (IOEN-): note whether it goes to the ASIC or is tied to a fixed level.
- Pin 14 (BUSRDY-): connected or not.

### Tracing results (2026-11-11)

Continuity checks on the original modem, from the J4 pads (and J1 for
pins 49/50) to U501. Pins 18-20 were used as a control and beeped, so
the pin numbering and the method are sound.

J4's pads carry solder bridges left from desoldering: pins 49 and 50
beeped together at J4 but not at J1, which was never desoldered. A
bridge can cause a false beep, not a false silence, so the "reaches
U501" results for pins 10 and 21 were rechecked at J1 and both hold.

| Slot pin | Result | Conclusion |
|----------|--------|------------|
| 10 (SLOT CS-) | Reaches U501 (one pin) | The modem uses the system's select |
| 18, 19, 20 (A0-A2) | Reach U501 | Register select, as expected |
| 37-43 (A3-A9) | No connection to U501 | The modem cannot decode its own address, so the 486c pre-decodes SLOT CS-. **Decoder not needed** |
| 21 (COMMCLK) | Reaches U501 | The modem took its clock from the slot. **Oscillator probably not needed**; confirm a clock is running on the machine |
| 49 (SLOT IOEN-) | No continuity to anything, and open circuit to ground and +5V in resistance mode, checked at J1 | The modem leaves IOEN- unconnected, so the 486c does not need it for a COM device. The card leaves it unconnected too |
| 14 (BUSRDY-) | No continuity to U501 (resistance to ground and +5V not measured) | The modem's bus chip never requested wait states, so it ran at the slot's normal bus timing. The card leaves pin 14 unconnected |

Still to settle on the running machine (Phase 0a): SLOT RST polarity on
pin 17 and a running clock on pin 21. The pre-decode conclusion rests on
the modem; the analyzer capture of SLOT CS- remains the confirmation.

---

## Phase 0b: UART on the Bus (no ESP32)

**Goal:** The 486c sees a working COM2. No firmware involved.

Wire the 16550 and the IRQ gate; leave pin 49 (IOEN-) unconnected. Leave the serial side
unconnected except SOUT looped to SIN, and CTS-/DSR-/DCD- tied low.

Tests:

1. `DEBUG`: `O 2FF 55` then `I 2FF` reads `55` (scratch register).
   Repeat with `AA`.
2. BIOS lists COM2 at POST (or `DEBUG` `D 40:0` shows `F8 02` in the
   second word).
3. A terminal program on COM2 echoes typed characters through the
   SOUT-SIN loop. This exercises interrupts.

Outcomes:

- Scratch register reads `FF` -> check IOEN- handling, then SLOT CS- and
  address wiring on the analyzer.
- Scratch works but no echo -> clock on XIN, or the IRQ path (OUT2- gate,
  EISA IRQ assignment).
- Hang or POST error -> bus contention; recheck CS2- and strobes.

---

## Phase 1: ESP32 Serial Link

**Goal:** Characters typed in a DOS terminal reach the ESP32 and echo back.

- Remove the loop; connect SOUT/SIN/RTS-/CTS- through the level shifter.
- Firmware: UART echo at a fixed rate (e.g. 9600 8N1), hardware flow control on.
- Then add baud tracking from BAUDOUT- and test at 2400, 19200, 57600, 115200.
- Run from slot power and check the 5V rail under WiFi load.
- Fit the external antenna (U.FL pigtail to RP-SMA) from this phase on,
  so WiFi range and TX power are tested as they will be used. Compare
  signal strength with the case closed.

Quick win: flashing an existing ESP32 WiFi modem firmware such as Zimodem
at this point gives a working modem and validates the hardware, before
writing any custom AT code.

---

## Phase 2: WiFi Bridge

**Goal:** Data flows between the DOS terminal and a TCP socket.

- ESP32 connects to a configured WiFi AP (credentials set via AT commands,
  stored in NVS)
- `ATDT<host>:<port>` opens a TCP connection
- Data mode: bytes flow bidirectionally between UART and socket
- Honour RTS-/CTS- flow control in both directions
- `+++` with guard time returns to command mode

---

## Phase 3: AT Command Set

**Goal:** Hayes-compatible command set for terminal software (Telix, Procomm, etc.)

Minimum commands:
- `AT` -> `OK`
- `ATZ` -> reset, `OK`
- `ATE0/ATE1` -> echo off/on
- `ATDThost:port` -> open TCP connection (`CONNECT <rate>`, `NO CARRIER`, `BUSY`)
- `ATH` -> hang up (close connection)
- `ATO` -> return to data mode
- `ATS0=1` -> auto-answer (listen mode)
- `+++` -> escape to command mode
- WiFi setup commands (SSID/password)

Modem control lines:
- DCD- follows connection state
- DTR- drop hangs up
- RI- pulses on an incoming connection

---

## Phase 4: Polish

- Final card PCB in the original modem's form factor, with the shield mounting
- Rear plate for the phone-jack opening carrying the RP-SMA bulkhead and
  the RJ12 display jack
- External OLED status display: I2C driver, status screen, and firmware
  that tolerates the display being absent or unplugged while running
- Telnet option negotiation, phonebook of host aliases
- Optional: dial and connect sounds through the system speaker via MSPKDRV (pin 25)

---

## Alternative Not Chosen: ESP32 Directly on the Bus

Having the ESP32 emulate the 16550 registers itself would save one chip,
but:

- An ISA read needs data roughly 400 ns after IOR- falls, which is marginal
  for an ESP32 polling GPIO, and needs a hardware wait-state circuit on
  BUSRDY- (pin 14) to be dependable.
- It needs about 18 GPIOs, three 74LVC245s, hardware gating of the data
  transceiver to prevent contention, and a core dedicated to polling.
- All 16550 behaviour (divisor latch, loopback, interrupt priorities,
  FIFO) has to be re-implemented and debugged against DOS software.

A Pico W would suit that approach better than an ESP32, since RP2040 PIO
handles ISA cycles with wait states (as PicoGUS and PicoMEM do).

---

## Key Risks

1. **486c slot may differ from the LTE Lite slot** — signal directions, COMMCLK and SLOT CS- pre-decode all rest on this; Phase 0a checks it
2. **IOEN- behaviour** — undocumented; the original modem leaves pin 49 unconnected and the card copies that, with a driven buffer as the fallback if reads return `FF`
3. **Pin numbering and orientation** — odd/even per the modem silkscreen, but check ground/+5V pads before ordering a PCB; a mirrored footprint puts +5V on signal pins
4. **Power** — WiFi TX bursts versus a 350 mA budget
5. **ESP32 5V tolerance** — every 16550 output goes through 3.3V-powered LVC parts
6. **Signal integrity** — three ground pins and a fine-pitch connector; keep bus wiring short
7. **Phone line in the display jack** — an RJ12 in a phone-jack opening invites it; ring voltage would destroy the card
8. **Rear opening not yet measured** — the plate, connector positions and pigtail length all depend on it

## Shopping List

- [ ] Calipers, multimeter
- [ ] Logic analyzer, 8 channels, 24 MHz or better
- [ ] Custom breakout PCB for the original 1.27 mm receptacle (no off-the-shelf adapter fits the keyed header)
- [x] 16C550 UART: TL16C550CFNR (PLCC-44) x2 — ordered from Mouser 2026-11-11
- [x] PLCC44-DIP40 V2.0 adapter with "flash"/"51" jumpers — on hand
- [x] PLCC extraction tool — on hand
- [x] 74HCT125 (IRQ gate; IOEN- buffer only as a fallback): SN74HCT125NE4 x2 — ordered from Mouser 2026-11-11
- [x] 5V -> 3.3V buffer for the ESP32 inputs: SN74LVC245AN — on hand
- [x] ESP32 dev board — on hand. The external antenna needs a U.FL
      connector (WROOM-32U type); confirm this board has one before the
      antenna step
- [ ] U.FL to RP-SMA bulkhead pigtail and a 2.4 GHz RP-SMA antenna (buy as a matching pair) — deferred
- [ ] SSD1306 I2C OLED module, 128x64
- [ ] RJ12 (6P6C) jack, RJ12 cable, a second jack or breakout for the display end
- [ ] 100 ohm resistors, 4.7K pull-ups and ESD protection diodes for the display lines
- [ ] Plate material for the phone-jack opening (3D print or sheet metal)
- [x] 1.8432 MHz oscillator (only if pin 21 has no clock): ECS-100AX-018, 5V DIP-14 can — ordered from Mouser 2026-11-11
- [x] Address decoder (only if SLOT CS- is not pre-decoded): CD74HCT688EE4, DIP-20 — ordered from Mouser 2026-11-11
- [x] Inverter (only if SLOT RST is active low): SN74HCT04N — ordered from Mouser 2026-11-11
- [x] 470 uF 25V electrolytic x2 (Vishay MAL219056471E3; fit one only) — ordered from Mouser 2026-11-11
- [x] 100 nF X7R leaded x10 (Vishay K104K15X7RF5TL2) — ordered from Mouser 2026-11-11
- [ ] Breadboard, short jumpers, resistors (100 ohm, 4.7K, 10K)
