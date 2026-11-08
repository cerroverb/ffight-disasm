local done = false
sub = emu.add_machine_frame_notifier(function()
  if done then return end
  done = true
  for tag, port in pairs(manager.machine.ioport.ports) do
    for name, field in pairs(port.fields) do
      print(string.format("PORT %s | %s | mask=%x", tag, name, field.mask))
    end
  end
  manager.machine:exit()
end)
