import abc


class TicketServer:

    def buyTickets(self):
        pass


class TrailSystem(TicketServer):

    def buyTickets(self):
        print('call buy ticket api, give a ticket')


class Third12306(TicketServer):

    def __init__(self):
        super(Third12306, self)
        self._name = "12306"
        self._trailsystem = TrailSystem()

    def buyTickets(self):
        print(f"登录{self._name}App")
        print("校验身份")
        self._trailsystem.buyTickets()
        print("发送购买通知")


class ThirdAliFeiZhu(TicketServer):

    def __init__(self):
        super(ThirdAliFeiZhu, self)
        self._name = "飞猪"
        self._trailsystem = TrailSystem()

    def buyTickets(self):
        print(f"登录{self._name}App")
        print("校验身份")
        self._trailsystem.buyTickets()
        print("发送购买通知")


third12306Serice = Third12306()
third12306Serice.buyTickets()
print("=========")
thirdFeizhuApp = ThirdAliFeiZhu()
thirdFeizhuApp.buyTickets()