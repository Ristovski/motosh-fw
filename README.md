# motosh-fw
This project aims to reverse engineer the firmware present on the Motorola Sensorhub - a [STM32](https://www.st.com/en/microcontrollers-microprocessors/stm32-32-bit-arm-cortex-mcus.html)
MCU inside most Motorola smartphones.

This MCU handles non-stop polling and processing of sensor data with the ability to send an interrupt to the smartphones CPU under
specific conditions (also known as `Moto Actions` or `Moto Gestures`).

## Documentation and resources
- STM32 Cortex-M0 programming manual: [pdf](https://www.st.com/resource/en/programming_manual/dm00104451-cortexm0-programming-manual-for-stm32l0-stm32g0-stm32wl-and-stm32wb-series-stmicroelectronics.pdf)  
- STM32L0x1 family reference manual: [pdf](https://www.st.com/resource/en/reference_manual/dm00108282-ultralowpower-stm32l0x1-advanced-armbased-32bit-mcus-stmicroelectronics.pdf)
- BMI160 datasheet: [pdf](https://www.mouser.com/datasheet/2/783/BST-BMI160-DS000-1509569.pdf)  
- AK09912C datasheet: [pdf](https://www.digikey.com/htmldatasheets/production/1746545/0/0/1/AK09912.pdf)
- [Wiki pages](https://github.com/Ristovski/motosh-fw/wiki/)

The sensorhub communicates with the kernel via SPI - the driver can be found [here](https://github.com/MotorolaMobilityLLC/kernel-msm/tree/nougat-7.0.0-release-potter-n/drivers/misc/stml0xx).  
The Android HAL and accompanying `motosh` binary (used for flashing firmware) are released by Motorola
[here](https://github.com/MotorolaMobilityLLC/hardware-moto-sensors/) under the respective `motosh_bin` and `motosh_hal` directories.

You can grab your own `sensorhubfw.bin` by copying it from `/etc/firmware/sensorhubfw.bin`.
> Warning: do note your firmware may _differ_ from the one included in this repository, as it has not yet been confirmed whether the firmware differs across devices.
A couple leaked schematics have shown drastic changes of the pinouts which means different functionality. 

## Current progress

- Very basic reverse engineering done (to be documented)
- Ability to boot the stock firmware in [Renode](https://renode.io/) (see [simulating](#simulating))
  - **Can be debugged with `gdb`** (no symbols though)
  - Appears to boot and attempt to access sensors
  - Model incomplete
    - Some internal functionality missing or partial ([RCC](https://wiki.st.com/stm32mpu/wiki/RCC_internal_peripheral) etc)
    - No sensors modeled yet
- Ability to boot custom firmware in Renode
  - Can be used to test if the sensorhub model is correct
  - Basic STM32L0 examples work
  - NVIC/SysTick/GPIO and timers functional
  - Weird bug where calling `__aeabi_uidiv` calls `__exidx_end` which then executes code out of bounds
    - This makes setting up UART (and probably a lot more stuff) impossible

## Installation
```
# clone main repo
git clone https://github.com/Ristovski/motosh-fw
# clone `libopencm3` under the `thirdparty/libopencm3` subdirectory
cd motosh-fw/thirdparty
git clone https://github.com/libopencm3/libopencm3 --depth=1
# build `libopencm3` for the `stm32/L0` target (make sure you have an arm cross-compiler working (`export PATH=$PATH:/path/to/cross/gcc/bin/`))
cd libopencm3
make TARGETS=stm32/l0
cd ../../
```

> Optionally, if you would like to emulate firmware, install [Renode](https://github.com/renode/renode/releases).
> Linux users can use the `portable` releases - just make sure to set your `PATH` accordingly.

## Building
Copy `cross_file.txt.example` to `cross_file.txt` and edit the `prefix` variable to point to your cross-compiler.

```
meson --cross-file cross_file.txt build && cd build
ninja
```

This will produce the following two files:  
`motosh` - ELF file containing symbols - useful for debugging under `gdb`  
`motosh.bin` - pure binary version generated with `objcopy -O binary motosh motosh.bin`

## Tools
![1616692920](https://user-images.githubusercontent.com/994445/112535247-597a2300-8dac-11eb-8107-4c69947e6bc3.png)
![1616700358](https://user-images.githubusercontent.com/994445/112535264-5da64080-8dac-11eb-9daa-a3827145b95d.png)


## Simulating
With [Renode](https://renode.io/) it is possible to simulate the official Moto sensorhub firmware (included at `fw/sensorhubfw.bin`)
to the point where it boots and attempts to communicate with the (non-existent) sensors.


![out](https://user-images.githubusercontent.com/994445/112535414-90503900-8dac-11eb-969c-49ed733d7c75.gif)


There are two models included in the `sim` directory, `motosh.{repl,resc}` - which is meant to be as close to the official MCU as possible
and `customfw.{repl,resc}` - meant to be used as a "playground" for testing the custom firmware and general accuracy of the Renode simulator.

> TODO: More Renode documentation.

To run the official firmware in the simulator, `cd` into the `sim` directory and run `FW=fw/sensorhubfw.bin renode motosh.resc`.

To run the custom firmware in the simulator, run `ninja install && ninja sim` inside the `build` directory to first copy the binary firmware into
the right place and then launch Renode.
