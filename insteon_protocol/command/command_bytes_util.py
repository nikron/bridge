class CMDS():
    def __init__(self, cmd1, cmd2=None):
        self.cmd1 = cmd1
        self.cmd2 = cmd2
        if self.cmd2:
            self.both = cmd1 + cmd2
            self.variable = True

        else:
            self.both = cmd1
            self.variable = False

    def __eq__(self, other):
        return self.both == other.both

    def __cmp__(self, other):
        return self.both.__cmp__(other.__both__)

    def __hash__(self):
        return hash(self.both)

class CommandBytesMap():
    def __init__(self, cmdbytes, call=True):
        self.variable = {cmd for cmd in cmdbytes if cmd.variable}
        self.static = {cmd for cmd in cmdbytes if not cmd.variable}

        self.call = call
        self.objs = {}

    def register(self, cmd, obj):
        if cmd in self.variable or cmd in self.static:
            self.objs[cmd] = obj

        #maybe raise an error if it isn't

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
            obj = self.objs[cmd1]

            if self.call:
                return obj(cmd2)
            else:
                return obj
