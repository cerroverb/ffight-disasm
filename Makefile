# Build and verify. The build reads only src/; the ROM is used by tools/gen.py and the verifier never needs it.
AS      = m68k-linux-gnu-as -m68000 --register-prefix-optional
LD      = m68k-linux-gnu-ld
OBJCOPY = m68k-linux-gnu-objcopy

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
