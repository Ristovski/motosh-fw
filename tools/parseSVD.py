#!/usr/bin/env python3

import os
import pysvd
import argparse
from enum import Enum
import xml.etree.ElementTree as ET

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("File [%s] does not exist!" % arg)
    else:
        return open(arg, 'r')

ENDC = '\033[m'
TGREEN = '\033[32m'
TYELLOW = '\033[33m'

parser = argparse.ArgumentParser(description="Parse a SVD file")
parser.add_argument('input_file', type=lambda x: is_valid_file(parser, x), help="input SVD")
parser.add_argument('--peripherals', action='store_true', help="dump peripherals")
parser.add_argument('--registers', action='store_true', help="dump registers")
parser.add_argument('--interrupts', action='store_true', help="dump interrupts")
parser.add_argument('-r', '--renode-output', action='store_true', help="[TODO] generate Renode definitions where applicable")
parser.add_argument('-o', '--output-file', dest='outfile', help="write output to file")
parser.add_argument('-d', '--debug', action='store_true', help="Enable debug output (stdout)")

args = parser.parse_args()

def DEBUG(arg):
	if(args.debug): print(arg)

def PRINT_GREEN(arg):
	print(TGREEN + arg + ENDC)
def PRINT_YELLOW(arg):
	print(TYELLOW + arg + ENDC)

DEBUG("WARN: Debug output enabled!");

print("Loading SVD...")

root = ET.parse(args.input_file).getroot()
device = pysvd.element.Device(root)

print("Device: {}, description: {}, reg. size: {}bits".format(device.name, device.description, device.size))
print("Peripherals: {}".format(len(device.peripherals)))

def dump_peripherals(device):
	print("Dumping peripheral list...\n")

	# Find longest name of peripheral
	maxlen = max([(len(x.name)) for x in device.peripherals])

	for peripheral in device.peripherals:
		peripheral_base_addr = peripheral.baseAddress
		size = peripheral.addressBlocks[0].size
		peripheral_end_addr = peripheral_base_addr + size

		print("{name:>{maxlen}} @ 0x{base_addr:X} - 0x{end_addr:X} (+0x{size:X}) [{desc}]".format(
			maxlen = maxlen,
			name = peripheral.name,
			base_addr = peripheral_base_addr,
			end_addr = peripheral_end_addr,
			size = size,
			desc = peripheral.description if hasattr(peripheral, 'description') else ""
		))

def dump_registers(device):
	print("Dumping registers...\n")

	# Find longest field name in all registers
	"""maxlen = 0
	for peripheral in device.peripherals:
		for register in peripheral.registers:
			for field in register.fields:
				size = len(field.name) + len(register.name) + len(peripheral.name)
				if size > maxlen:
					maxlen = size"""

	for peripheral in device.peripherals:
		peripheral_base_addr = peripheral.baseAddress
		size = peripheral.addressBlocks[0].size
		peripheral_end_addr = peripheral_base_addr + size

		# Print peripheral device
		PRINT_GREEN("{} @ 0x{:X} - 0x{:X} [+0x{:X}] [{}]".format(peripheral.name, peripheral_base_addr, peripheral_end_addr, size, peripheral.description if hasattr(peripheral, 'description') else ""))

		maxlen = 0
		"""for register in peripheral.registers:
			for field in register.fields:
				size = len(field.name) + len(register.name) + len(peripheral.name)
				if size > maxlen:
					maxlen = size + 4"""

		for register in peripheral.registers:
			offset = register.addressOffset
			abs_address = peripheral_base_addr + offset

			maxlen = 0
			for field in register.fields:
				size = len(field.name) + len(register.name) + len(peripheral.name)
				if size > maxlen:
					maxlen = size + 8

			PRINT_YELLOW("\t {}:{} @ 0x{:X} (+0x{}) ({})".format(peripheral.name, register.name, abs_address, offset, register.description if hasattr(register, 'description') else "").expandtabs(2))

			for field in register.fields:
				full_name = "{}:{}:{}".format(peripheral.name, register.name, field.name)
				field_offset = field.bitOffset
				field_width = field.bitWidth + field_offset - 1
				byte_offset = int(field_offset/8)
				bit_offsets = "{}:{}".format(field_width, field_offset)

				print("\t\t {name:>{maxlen}} @ (+{byte_offset:^2}B) [{bit_offset:^5}] ({desc})".format(
					name = full_name,
					maxlen = maxlen,
					byte_offset = byte_offset,
					bit_offset = bit_offsets,
					field_offset = field_offset,
					desc = field.description if hasattr(field, 'description') else ""
				).expandtabs(2))

			print("")

def dump_interrupts(device):
	print("Dumping interrupts...\n")

	for peripheral in device.peripherals:
		peripheral_base_addr = peripheral.baseAddress
		size = peripheral.addressBlocks[0].size
		peripheral_end_addr = peripheral_base_addr + size

		if(hasattr(peripheral, 'interrupts')):
			if(len(peripheral.interrupts) > 0):
				PRINT_GREEN("{} @ 0x{:X} - 0x{:X} [+0x{:X}] [{}]".format(peripheral.name, peripheral_base_addr, peripheral_end_addr, size, peripheral.description))

				for interrupt in peripheral.interrupts:
					print("\t IRQ:{} - {} [{}]".format(interrupt.value, interrupt.name, interrupt.description).expandtabs(2))

				print("")

if(args.peripherals):
	dump_peripherals(device)
if(args.registers):
	dump_registers(device)
if(args.interrupts):
	dump_interrupts(device)
