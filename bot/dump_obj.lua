local p = manager.machine.ioport.ports
local coin, start = p[":IN0"].fields["Coin 1"], p[":IN0"].fields["1 Player Start"]
local R = p[":IN1"].fields["P1 Right"]
local mem = manager.machine.devices[":maincpu"].spaces["program"]
local f = 0
sub = emu.add_machine_frame_notifier(function()
  f = f + 1
  coin:set_value((f % 300 < 4) and 1 or 0)
  start:set_value((f % 300 >= 30 and f % 300 < 34) and 1 or 0)
  R:set_value((f > 1300 and f % 60 < 40) and 1 or 0)
  if f >= 1500 and f % 180 == 0 then
    print("---- f=" .. f)
    for i = 0, 14 do
      local a = 0xFF8568 + i * 0xC0
      local s = ""
      for k = 0, 0x2F, 2 do s = s .. string.format("%04x ", mem:read_u16(a + k)) end
      if mem:read_u16(a) ~= 0 then print(string.format("slot%02d %s", i, s)) end
    end
  end
  if f > 2600 then manager.machine:exit() end
end)
