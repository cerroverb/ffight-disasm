# Build and verify. The build reads only src/; the ROM is used by tools/gen.py and the verifier never needs it.
CROSS  ?= m68k-linux-gnu-
export CROSS
AS      = $(CROSS)as -m68000 --register-prefix-optional
LD      = $(CROSS)ld
OBJCOPY = $(CROSS)objcopy

all: verify

build/ffight.o: src/ffight.s
	@mkdir -p build
	$(AS) -al=build/ffight.lst -o $@ $<

build/ffight.bin: build/ffight.o
	$(LD) -n -Ttext=0 -e 0 -o build/ffight.elf $<
	$(OBJCOPY) -O binary -j .text build/ffight.elf $@

verify: build/ffight.bin
	python3 -I verify/verify_maincpu.py build/ffight.bin
	python3 -I verify/check_coverage.py build/ffight.lst traces/*.txt

clean:
	rm -rf build/ffight.*

.PHONY: all verify clean
