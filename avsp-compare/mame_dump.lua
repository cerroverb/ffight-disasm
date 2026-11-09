-- MAME autoboot script: replays a cps2recomp input movie on a CPS2 set and writes the
-- 68000 work RAM (0xFF0000-0xFFFFFF, 65536 bytes) after every frame, one frame after another.
--
-- Settings come from the environment:
--   AVSP_MOVIE   cps2recomp movie (lines: frame p1 p2 [p3 [p4]], pressed bits in hex; '#' comments)
--   AVSP_OUT     output file for the RAM frames
--   AVSP_FRAMES  number of frames to run, then exit
--   AVSP_SHIFT   movie frame N is applied at MAME frame N + AVSP_SHIFT (default 0)
--
-- The port words are built the same way as cps2recomp's Machine::Input (machine/machine.cpp),
-- then written to MAME's :IN0 :IN1 :IN2 fields by mask, so both sides see the same input lines.

local movie_path = os.getenv("AVSP_MOVIE")
local out_path = os.getenv("AVSP_OUT")
local frames = tonumber(os.getenv("AVSP_FRAMES") or "")
local shift = tonumber(os.getenv("AVSP_SHIFT") or "0") or 0
if not out_path or not frames then
	print("mame_dump.lua: AVSP_OUT and AVSP_FRAMES must be set")
	manager.machine:exit()
	return
end

-- movie: sorted list of {frame, {p1, p2, p3, p4}}
local changes = {}
if movie_path and movie_path ~= "" then
	local f = assert(io.open(movie_path, "r"))
	for line in f:lines() do
		if line:sub(1, 1) ~= "#" then
			local nums = {}
			for word in line:gmatch("%S+") do
				nums[#nums + 1] = word
			end
			if #nums >= 3 then
				local p = {}
				for i = 1, 4 do
					p[i] = nums[i + 1] and tonumber(nums[i + 1], 16) or 0
				end
				changes[#changes + 1] = {tonumber(nums[1]), p}
			end
		end
	end
	f:close()
	table.sort(changes, function(a, b) return a[1] < b[1] end)
end

local machine = manager.machine
local space = machine.devices[":maincpu"].spaces["program"]
local ports = {machine.ioport.ports[":IN0"], machine.ioport.ports[":IN1"], machine.ioport.ports[":IN2"]}
for i, tag in ipairs({":IN0", ":IN1", ":IN2"}) do
	if not ports[i] then
		print("mame_dump.lua: no port " .. tag)
		machine:exit()
		return
	end
end
-- Only these bits are driven; IN2's low byte (EEPROM, test, service) is left to MAME.
local driven = {0xFFFF, 0xFFFF, 0xFF00}

local out = assert(io.open(out_path, "wb"))
local pads = {0, 0, 0, 0}
local next_change = 1
local frame = 0
local unmapped = {0, 0, 0}

local function port_words(p)
	local p1, p2, p3, p4 = p[1], p[2], p[3], p[4]
	local w0 = (p1 & 0x7F) | ((p2 & 0x7F) << 8)
	local w1 = ((p1 >> 7) & 7) | (((p2 >> 7) & 3) << 4) | (p3 & 0x7F) | ((p4 & 0x7F) << 8)
	local w2 = 0
	if p1 & 0x0400 ~= 0 then w2 = w2 | 0x0100 end
	if p2 & 0x0400 ~= 0 then w2 = w2 | 0x0200 end
	if p3 & 0x0400 ~= 0 then w2 = w2 | 0x0400 end
	if p4 & 0x0400 ~= 0 then w2 = w2 | 0x0800 end
	if p1 & 0x0800 ~= 0 then w2 = w2 | 0x1000 end
	if p2 & 0x0800 ~= 0 then w2 = w2 | 0x2000 end
	if p3 & 0x0800 ~= 0 then w2 = w2 | 0x4000 end
	if p4 & 0x0800 ~= 0 then w2 = w2 | 0x8000 end
	if p2 & 0x0200 ~= 0 then w2 = w2 | 0x4000 end
	return {w0, w1, w2}
end

local function apply_inputs(f)
	local movie_frame = f - shift
	while next_change <= #changes and changes[next_change][1] <= movie_frame do
		pads = changes[next_change][2]
		next_change = next_change + 1
	end
	local words = port_words(pads)
	for i = 1, 3 do
		local covered = 0
		for _, field in pairs(ports[i].fields) do
			if field.mask & driven[i] ~= 0 then
				covered = covered | field.mask
				if words[i] & field.mask ~= 0 then
					field:set_value(1)
				else
					field:set_value(0)
				end
			end
		end
		if words[i] & driven[i] & ~covered ~= 0 then
			unmapped[i] = unmapped[i] + 1
		end
	end
end

apply_inputs(0)

local function on_frame()
	out:write(space:read_range(0xFF0000, 0xFFFFFF, 8))
	frame = frame + 1
	if frame >= frames then
		out:close()
		print(string.format("mame_dump.lua: %d frames written to %s", frame, out_path))
		print(string.format("mame_dump.lua: frames with input bits MAME has no field for: IN0 %d IN1 %d IN2 %d",
			unmapped[1], unmapped[2], unmapped[3]))
		machine:exit()
		return
	end
	apply_inputs(frame)
end

if emu.add_machine_frame_notifier then
	avsp_compare_sub = emu.add_machine_frame_notifier(on_frame)
else
	emu.register_frame_done(on_frame)
end
