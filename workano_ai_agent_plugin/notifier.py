from wazo_confd import bus, sysconfd

class AIAgentNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        pass

    def created(self, survey):
        pass

    def edited(self, survey):
        pass

    def deleted(self, survey):
        pass


def build_ai_agent_notifier():
    return AIAgentNotifier(bus, sysconfd)
