from insteon_protocol.command import command_bytes
class CommandBytesMap():
    def __init__(self):
        #self.cmdbytes = {getattr(command_bytes, cmdstr) for cmdstr in command_bytes.__all__ if getattr(command_bytes, cmdstr).is_variable()}
        self.objs = {}

    def register(self, cmd, obj):
        self.objs[cmd] = obj

    def get(self, insteon_command):
        cmd1 = insteon_command.cmd1
        cmd2 = insteon_command.cmd2
        obj = self.objs.get(cmd1 + cmd2)
        if obj:
            return obj
        else:
            func = self.objs[cmd1]
            return func(cmd2)
