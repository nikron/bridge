class CMDS():
    def __init__(self, cmd1, cmd2=None):
        self.cmd1 = cmd1
        self.cmd2 = cmd2
        if self.cmd2:
            self.both = cmd1 + cmd2
        else:
            self.both = cmd1

    def __eq__(self, other):
        return self.both == other.both

    def __cmp__(self, other):
        return self.both.__cmp__(other.__both__)

    def __hash__(self):
        return hash(self.both)

class CommandBytesMap():
    def __init__(self):
        #self.cmdbytes = {getattr(command_bytes, cmdstr) for cmdstr in command_bytes.__all__ if getattr(command_bytes, cmdstr).is_variable()}
        self.objs = {}

    def register(self, cmd, obj):
        self.objs[cmd] = obj

    def get(self, insteon_command):
        """Will need to eventually store things based on product name too."""
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
