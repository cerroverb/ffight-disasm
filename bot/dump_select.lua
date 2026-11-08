-- Dumps 68000 work RAM (0xFF0000-0xFFFFFF) every DUMP_EVERY frames to DUMP_DIR/ram_FRAME.bin
-- with a snapshot, after coin + start, optionally holding P1 Right from TAP_FRAME for TAP_LEN frames.
local p = manager.machine.ioport.ports
local coin, start = p[":IN0"].fields["Coin 1"], p[":IN0"].fields["1 Player Start"]
local R = p[":IN1"].fields["P1 Right"]
local mem = manager.machine.devices[":maincpu"].spaces["program"]
local tap = tonumber(os.getenv("TAP_FRAME") or "0")
local taplen = tonumber(os.getenv("TAP_LEN") or "6")
local every = tonumber(os.getenv("DUMP_EVERY") or "60")
local dir = os.getenv("DUMP_DIR")
local f = 0
sub = emu.add_machine_frame_notifier(function()
  f = f + 1
  local c = f % 300
  coin:set_value((c < 4) and 1 or 0)
  start:set_value((c >= 30 and c < 34) and 1 or 0)
  R:set_value((tap > 0 and f >= tap and f < tap + taplen) and 1 or 0)
  if f % every == 0 then
    local out = io.open(string.format("%s/ram_%05d.bin", dir, f), "wb")
    for a = 0xFF0000, 0xFFFFFF, 4 do out:write(string.pack(">I4", mem:read_u32(a))) end
    out:close()
    manager.machine.video:snapshot()
  end
end)
