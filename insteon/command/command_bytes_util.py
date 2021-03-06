"""
Utilities for creating CMDS constants and using them to interact
with the INSTEON protocol.
"""
import logging

class CMDS():
    """
    Create an object that guesses the attributes of command bytes.

    :param relative: Whether the response from a device to this command byte would not 
    conform to the general INSTEON protocol.
    :type relative: bool
    """

    def __init__(self, cmd1, cmd2 = None, **kwargs):
        self.cmd1 = cmd1
        self.cmd2 = cmd2
        if self.cmd2:
            self.both = cmd1 + cmd2
            self.variable = False

        else:
            self.both = cmd1
            self.variable = True

        self.relative = kwargs.get('relative', False)

    def is_variable(self):
        """
        If the second byte changes the meaning of the command bytes.
        """
        return self.variable

    def is_relative(self):
        """
        Whether the response is relative to this.
        """
        return self.relative

    def __eq__(self, other):
        return self.both == other.both

    def __cmp__(self, other):
        return self.both.__cmp__(other.__both__)

    def __hash__(self):
        return hash(self.both)

class CommandBytesMap():
    """
    Map objects to command bytes.
    """

    def __init__(self, call):
        self.call = call
        self.objs = {}
        self.relative = set()

    def register(self, cmd, obj, relative_cmd = None):
        """
        Register an object with a command byte.
        """
        if not cmd.is_relative():
            self.objs[cmd] = obj

        else:
            if cmd in self.relative:
                if relative_cmd is None:
                    self.objs[cmd][1][relative_cmd] = obj
                else:
                    self.objs[cmd][0] = obj
            else:
                if relative_cmd is None:
                    self.objs[cmd] = (obj, {})
                else:
                    self.objs[cmd] = (None, obj)

    def get(self, insteon_command, relative_cmd = None):
        """
        Retrieve the object with a structure(s) that have cmd1 and cmd2.
        """
        cmd1 = insteon_command.cmd1
        cmd2 = insteon_command.cmd2
        cmd = CMDS(cmd1, cmd2)

        logging.debug("Attempting to retrieve object with key {0}.".format(str(cmd.both)))

        if relative_cmd is not None:
            rcmd =  CMDS(relative_cmd.cmd1, relative_cmd.cmd2)
            logging.debug(rcmd.both)

        obj = self.objs.get(cmd, None)
        if obj:
            if relative_cmd is None:
                return obj
            else:
                if rcmd in obj[1]:
                    return obj[1][rcmd]
                elif self.call:
                    return obj[0](rcmd)

        else:
            cmd = CMDS(cmd1)
            obj = self.objs[cmd]

            if self.call:
                return obj(cmd2)
            else:
                return obj
