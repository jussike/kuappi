# What?
Kuappi is a small hobby python project that reads data from the sensor and controls the device according to predefined limits.
It tries to be modular enough that you can easily add a support for different hardwares and protocols.

# Why?
The thermostat of my fridge is broken. I needed some way to control temperature.
And I thought that writing my own software would be fun.

# How?

You can set a RPi or similar for controlling devices. I'm currently controlling my fridge and ventilation unit.

## Currently supported protocols
    * 1-Wire
    * Bluetooth (via mitemp)
    * Zigbee (via mqtt)
    * Wemo switch
    * GPIO pins
    * Vallox over RS485
## Recommended hardware
    * Rpi 2 or newer

## What next?
    * Full instructions for setup
    * More controls for vallox
    * More unit tests
    * Alerts via email
    * Server software for showing graphs (already work in progress)

## How to set up RPi and zigbee?
    * https://lemariva.com/blog/2019/04/zigbee-xiaomi-sensors-using-raspberry-pi-without-gateway

# License
    * MIT
