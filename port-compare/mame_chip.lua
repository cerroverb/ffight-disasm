-- MAME autoboot script: logs every write of Final Fight's Z80 to the YM2151 (F000, F001) and the OKI (F002), one
-- line each: Z80 time in cycles of 3.579545 MHz, address, value. Environment: FF_CHIPLOG (output file). Run it with
-- FF_MOVIE, FF_FRAMES and FF_SHIFT as for mame_ram.lua by appending mame_ram.lua's input part, or on its own.
local zp = manager.machine.devices[":audiocpu"].spaces["program"]
local chiplog = assert(io.open(os.getenv("FF_CHIPLOG"), "w"))
ff_chiptap = zp:install_write_tap(0xf000, 0xf002, "ffchiptap", function(offset, data, mask)
  chiplog:write(string.format("%d %04x %02x\n", math.floor(manager.machine.time:as_double() * 3579545 + 0.5), offset, data & 0xff))
  chiplog:flush()
end)
