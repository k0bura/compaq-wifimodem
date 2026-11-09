# Compaq WiFi Modem Project

ESP32-based WiFi modem for the Compaq Portable 486c Enhanced Options Slot (50-pin proprietary ISA-like bus).

## Key Reference Files

- `reference/Compaq_Enhanced_Options_Slot_Reference.md` — 50-pin pinout and signal descriptions
- `reference/128984-001_Portable_486C_Reference_Guide_199111.pdf` — Full Compaq Portable 486c manual
- `reference/8977986.pdf` — Compaq LTE Lite service/expansion options guide
- `reference/photos/` — Photos of the slot header (J22) and the original Compaq modem, indexed in the slot reference file
- `PLAN.md` — Phased implementation plan (Phase 0-4)

## Project Status

Phase 0: Planning / hardware acquisition. No firmware written yet.

## Architecture

- A real 16C550 UART (5V) sits on the 50-pin Enhanced Options Slot at a standard COM port address (COM2 = 0x2F8, IRQ3)
- The ESP32 connects to the UART's serial side (TTL serial + modem control lines), with 3.3V-powered 74LVC parts shifting the UART's 5V outputs down
- ESP32 firmware bridges serial to WiFi TCP connections and implements the Hayes AT command set for DOS terminal software
- The ESP32 does not touch the bus; emulating the 16550 on the bus was considered and rejected (see PLAN.md)
- Slot signal directions come from the LTE Lite guide and are not yet verified on the 486c
