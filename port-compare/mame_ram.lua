-- MAME autoboot script: replays a cps2recomp input movie on Final Fight (CPS-1, cps1_3b inputs) and writes the
-- 68000 work RAM (FF0000-FFFFFF) after every frame. Environment: FF_MOVIE, FF_OUT, FF_FRAMES, FF_SHIFT.
-- Port words as cps2recomp's Machine::ReadCps1: IN1 = player 1 stick and buttons (bits 0-6) | player 2's << 8;
-- IN0 = coin 1, coin 2, start 1, start 2 from each player's kCoin (0x800) and kStart (0x400).
local movie_path = os.getenv("FF_MOVIE")
local out_path = os.getenv("FF_OUT")
local frames = tonumber(os.getenv("FF_FRAMES") or "")
local shift = tonumber(os.getenv("FF_SHIFT") or "0") or 0
local changes = {}
local f = assert(io.open(movie_path, "r"))
for line in f:lines() do
  if line:sub(1, 1) ~= "#" then
    local n = {}
    for w in line:gmatch("%S+") do n[#n + 1] = w end
    if #n >= 3 then changes[#changes + 1] = {tonumber(n[1]), {tonumber(n[2], 16), tonumber(n[3], 16)}} end
  end
end
f:close()
table.sort(changes, function(a, b) return a[1] < b[1] end)
local machine = manager.machine
local space = machine.devices[":maincpu"].spaces["program"]
local in0, in1 = machine.ioport.ports[":IN0"], machine.ioport.ports[":IN1"]
local out = assert(io.open(out_path, "wb"))
local pads, nxt, frame = {0, 0}, 1, 0
local function set(port, word, driven)
  for _, field in pairs(port.fields) do
    if field.mask & driven ~= 0 then field:set_value((word & field.mask) ~= 0 and 1 or 0) end
  end
end
local function apply(fr)
  while nxt <= #changes and changes[nxt][1] <= fr - shift do pads = changes[nxt][2]; nxt = nxt + 1 end
  local p1, p2 = pads[1], pads[2]
  set(in1, (p1 & 0x7F) | ((p2 & 0x7F) << 8), 0x7F7F)
  local w0 = ((p1 & 0x800) ~= 0 and 0x01 or 0) | ((p2 & 0x800) ~= 0 and 0x02 or 0) |
             ((p1 & 0x400) ~= 0 and 0x10 or 0) | ((p2 & 0x400) ~= 0 and 0x20 or 0)
  set(in0, w0, 0x33)
end
apply(0)
local function on_frame()
  out:write(space:read_range(0xFF0000, 0xFFFFFF, 8))
  frame = frame + 1
  if frame >= frames then out:close(); print("frames written " .. frame); machine:exit(); return end
  apply(frame)
end
if emu.add_machine_frame_notifier then ff_sub = emu.add_machine_frame_notifier(on_frame) else emu.register_frame_done(on_frame) end
