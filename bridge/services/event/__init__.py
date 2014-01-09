from select import select
import datetime
import logging

from bridge.services import BridgeService, BridgeMessage

class BridgeEvent():
    def __init__(self, time, message):
        self.time = time
        self.message = message
        self.next_time = None
        self.set_next_time()

    def set_next_time(self):
        event_today = datetime.datetime.combine(datetime.date.today(), self.time)
        if datetime.datetime.now() > event_today:
            self.next_time = event_today + datetime.timedelta(days=1)
        else:
            self.next_time = event_today

        logging.debug("Event set to fire at {0}.".format(self.next_time))


    def check(self):
        if self.next_time is None:
            return False

        if datetime.datetime.now() > self.next_time:
            self.set_next_time()
            return True
        else:
            return False

class EventService(BridgeService):
    def __init__(self, config, con):
        super().__init__("event", config, con)
        self.read_list = [self.hub_connection]
        self.events_que = [BridgeEvent(datetime.time(20,30,0), BridgeMessage.create_async('lights', 'turn_on', '1.89')),
            BridgeEvent(datetime.time(20,30,0), BridgeMessage.create_async('lights', 'turn_on', '1.67')),
            BridgeEvent(datetime.time(20,30,0), BridgeMessage.create_async('lights', 'turn_on', '1.30')),
            BridgeEvent(datetime.time(20,30,0), BridgeMessage.create_async('lights', 'turn_on', '1.1')),
            BridgeEvent(datetime.time(2,0,0), BridgeMessage.create_async('lights', 'turn_off', '1.89')),
            BridgeEvent(datetime.time(2,0,0), BridgeMessage.create_async('lights', 'turn_off', '1.67')),
            BridgeEvent(datetime.time(2,0,0), BridgeMessage.create_async('lights', 'turn_off', '1.1')),
            BridgeEvent(datetime.time(2,0,0), BridgeMessage.create_async('lights', 'turn_off', '1.30'))]

    def run(self):
        self.mask_signals()
        self.spinning = True
        logging.debug("Event service on.")

        while self.spinning:
            (read, _, _) = select(self.read_list, [], [], 1)
            if self.hub_connection in read:
                self.read_and_do_remote_request()

            for event in self.events_que:
                if event.check():
                    logging.debug("Doing some event action.")
                    self.hub_connection.send(event.message)
