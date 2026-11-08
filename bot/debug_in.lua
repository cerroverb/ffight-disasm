local p = manager.machine.ioport.ports
local R = p[":IN1"].fields["P1 Right"]
local coin = p[":IN0"].fields["Coin 1"]
local start = p[":IN0"].fields["1 Player Start"]
local mem = manager.machine.devices[":maincpu"].spaces["program"]
local f = 0
sub = emu.add_machine_frame_notifier(function()
  f = f + 1
  coin:set_value((f % 300 < 4) and 1 or 0)
  start:set_value((f % 300 >= 30 and f % 300 < 34) and 1 or 0)
  if f > 900 then R:set_value(1) end
  if f % 120 == 0 then
    print(string.format("f=%d IN1=%04x IN0=%04x x=%04x", f, p[":IN1"]:read(), p[":IN0"]:read(), mem:read_u16(0xFF8568 + 6)))
  end
  if f > 2400 then manager.machine:exit() end
end)
