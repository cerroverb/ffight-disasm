-- Final Fight player bot for coverage runs.
-- Reads object slots (layout from mame-rr beatemup-hitboxes.lua: 0xC0-byte objects,
-- players/enemies at 0xFF8568, bosses at 0xFF9528, HP at +0x18) plus fields found by
-- RAM dump: +0x00 active, +0x06 X, +0x0A depth.
-- Walks to the nearest enemy, attacks when lined up, otherwise walks right.
-- Keeps inserting coins and pressing start so it continues forever.
-- env: BOT_CHAR (0..2 Right presses on character select), BOT_SNAP (s), BOT_SEED
local p = manager.machine.ioport.ports
local function F(port, name) return p[port].fields[name] end
local coin, start = F(":IN0", "Coin 1"), F(":IN0", "1 Player Start")
local R, L = F(":IN1", "P1 Right"), F(":IN1", "P1 Left")
local U, D = F(":IN1", "P1 Up"), F(":IN1", "P1 Down")
local atk, jmp = F(":IN1", "P1 Button 1"), F(":IN1", "P1 Button 2")
local mem = manager.machine.devices[":maincpu"].spaces["program"]

local char = tonumber(os.getenv("BOT_CHAR") or "0")
local snap = 60 * tonumber(os.getenv("BOT_SNAP") or "60")
math.randomseed(tonumber(os.getenv("BOT_SEED") or "1"))

local function s16(v) if v >= 0x8000 then return v - 0x10000 end return v end
local function obj(a)
  return { on = mem:read_u8(a) ~= 0, x = mem:read_u16(a + 6), y = s16(mem:read_u16(a + 0x0A)),
           hp = s16(mem:read_u16(a + 0x18)) }
end

local f, stuck, lastx = 0, 0, 0
sub = emu.add_machine_frame_notifier(function()
  f = f + 1
  local want = {}
  local function set(field) want[field] = true end

  local c = f % 300
  if c < 4 then set(coin) end
  if c >= 30 and c < 34 then set(start) end
  if f > 400 and f < 400 + char * 20 and (f % 20) < 5 then set(R) end

  if f > 600 then
    local pl = obj(0xFF8568)
    local best, bd
    local function consider(a)
      local e = obj(a)
      if e.on and e.hp > 0 then
        local d = math.abs(e.x - pl.x) + 3 * math.abs(e.y - pl.y)
        if not bd or d < bd then best, bd = e, d end
      end
    end
    for i = 1, 14 do consider(0xFF8568 + i * 0xC0) end
    for i = 0, 7 do consider(0xFF9528 + i * 0xC0) end

    if best then
      local dx, dy = best.x - pl.x, best.y - pl.y
      if math.abs(dy) > 4 then if dy > 0 then set(D) else set(U) end end
      if math.abs(dx) > 0x28 then
        if dx > 0 then set(R) else set(L) end
      elseif math.abs(dy) <= 6 then
        if f % 16 < 2 then if dx > 0 then set(R) else set(L) end end   -- face it
        if f % 6 < 2 then set(atk) end
      end
    else
      if f % 200 < 190 then set(R) end
    end
    -- unstick: if X has not changed for 3 s, jump and wander
    if pl.x == lastx then stuck = stuck + 1 else stuck = 0 end
    lastx = pl.x
    if stuck > 180 then
      if f % 60 < 6 then set(jmp) end
      if f % 120 < 60 then set(U) else set(D) end
    end
    if f % 1500 < 4 then set(atk); set(jmp) end   -- special now and then
  end

  for _, x in ipairs({coin, start, R, L, U, D, atk, jmp}) do x:set_value(want[x] and 1 or 0) end
  if f % snap == 0 then manager.machine.video:snapshot() end
end)
