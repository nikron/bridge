from insteon_protocol.command.command_bytes import CMDS

class CommandBytesMap():
    def __init__(self):
        #self.cmdbytes = {getattr(command_bytes, cmdstr) for cmdstr in command_bytes.__all__ if getattr(command_bytes, cmdstr).is_variable()}
        self.objs = {}

    def register(self, cmd, obj):
        self.objs[cmd] = obj

    def get(self, insteon_command):
        cmd1 = insteon_command.cmd1
        cmd2 = insteon_command.cmd2
        cmd = CMDS(cmd1, cmd2)

        obj = self.objs.get(cmd)
        if obj:
            return obj
        else:
            cmd = CMDS(cmd1)
            func = self.objs[cmd1]
            return func(cmd2)
