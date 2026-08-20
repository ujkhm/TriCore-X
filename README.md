# Xeltri

> **Xeltri: a heterogeneous development board.**
> X = mixed heterogeneous cores, el = electronics, tri = three cores (MPU + MCU + FPGA).
> This board puts an FPGA, an MPU, and an MCU on one system. (in development)

#### Read the original Traditional Chinese version [here](README.zh-TW.md).

**Hackaday.io Project Page:** [Xeltri - Pick and Place Control Board](https://hackaday.io/project/206451-xeltri-pick-and-place-control-board)


---

### Project overview
This project is a main controller board built for a desktop pick-and-place (PnP) machine. The three cores — STM32H745XIH6 (MCU), XC7A35T-2CSG325C (FPGA), and V851S (MPU) — are locked in and work together. Expansion I/O so far: PCIe 2.1 ×2 (in a PCIe ×4 slot, wired to the FPGA) and a microSD card slot. Everything else is still TBD.

---

### How it started
I needed a pick-and-place machine, but buying one was too expensive, so I decided to build it myself. I was 15 when I started (25 June 2026). It began as a sudden “what if I just try?” thought, and I then committed to it as a long-term project. A lot of what this board needs is something I only know *what it is for*, not something I have actually designed before. I know this is hard, so please keep expectations modest — but it should not be terrible either.

---

### Board architecture and why these cores
Xeltri is built around STM32H745XIH6 (MCU), XC7A35T-2CSG325C (FPGA), and V851S (MPU). I chose this trio because I want to try mixed alignment: pure optical alignment for simple parts (0805, 0402, and similar packages), and a vision camera (OpenCV-style) for complex parts. I also want up-looking / down-looking cameras plus on-device AI for machine-health checks — that is why V851S is in the mix.

I am using pure optical alignment on simple parts because I want industrial on-the-fly (“flying shot”) speed, and the vision hardware that can actually do that is far too expensive. Optical alignment is much cheaper, but it needs real-time performance. The machine is meant to be a box-style CoreXY so it takes less floor space (like a Voron printer), which means a lot of structure and a lot of stepper motors to control. Closed-loop steppers with the servo drive in the motor base are too expensive for me, and the cheap ones are not fast enough. An FPGA can handle that and more — I want the finished machine to be strong, not merely usable. That is how this three-core combination ended up here.
