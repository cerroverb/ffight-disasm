# Build and verify. The build reads only src/; the ROM is used by tools/gen.py and the verifier never needs it.
CROSS  ?= m68k-linux-gnu-
export CROSS
AS      = $(CROSS)as -m68000 --register-prefix-optional
LD      = $(CROSS)ld
OBJCOPY = $(CROSS)objcopy
ZCROSS ?= z80-unknown-coff-
export ZCROSS
# The expected chip hashes come from MAME itself, not from this repository.
MAME_COMMIT = f09e0805da149cb15bd1cd777fbbcc65640d7866
CPS1_CPP    = build/mame_src/$(MAME_COMMIT)/cps1.cpp

all: verify

build/ffight.o: src/ffight.s
	@mkdir -p build
	$(AS) -al=build/ffight.lst -o $@ $<

build/ffight.bin: build/ffight.o
	$(LD) -n -Ttext=0 -e 0 -o build/ffight.elf $<
	$(OBJCOPY) -O binary -j .text build/ffight.elf $@

build/sound.o: src/sound.s
	@mkdir -p build
	$(ZCROSS)as -march=z80 -al=build/sound.lst -o $@ $<

build/sound.bin: build/sound.o
	$(ZCROSS)ld -Ttext=0 -o build/sound.elf $<
	$(ZCROSS)objcopy -O binary -j .text build/sound.elf $@

$(CPS1_CPP):
	@mkdir -p $(dir $@)
	curl -fsSL -o $@ https://raw.githubusercontent.com/mamedev/mame/$(MAME_COMMIT)/src/mame/capcom/cps1.cpp

verify: build/ffight.bin build/sound.bin $(CPS1_CPP)
	python3 -I verify/verify_maincpu.py build/ffight.bin $(CPS1_CPP)
	python3 -I verify/check_coverage.py build/ffight.lst traces/*.txt
	python3 -I verify/verify_audiocpu.py build/sound.bin $(CPS1_CPP)
	python3 -I verify/check_coverage.py --z80 build/sound.lst traces/z80/*.txt

clean:
	rm -rf build/ffight.* build/sound.*

.PHONY: all verify clean
