-- MAME autoboot script: sends every sound command 0x00-0xff to the Z80 sound CPU.
-- The command is written to the 68000 side of the sound latch (0x800181, cps1_soundlatch_w low
-- byte, MAME cps1.cpp main_map) for HOLD frames, then the game's own writes (0xff while idle)
-- take over for the rest of PERIOD frames. Starts after BOOT frames. Exits after the last command.
-- env: SND_PERIOD (frames per command, default 180)
local main = manager.machine.devices[":maincpu"].spaces["program"]
local BOOT, HOLD = 600, 6
local PERIOD = tonumber(os.getenv("SND_PERIOD") or "180")
local frame = 0
emu.register_frame_done(function()
  frame = frame + 1
  if frame < BOOT then return end
  local cmd = (frame - BOOT) // PERIOD
  if cmd > 0xff then manager.machine:exit() return end
  if (frame - BOOT) % PERIOD < HOLD then main:write_u8(0x800181, cmd) end
end)
