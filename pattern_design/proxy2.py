import abc


class SellerService:

    def sellerHourse(self):
        pass


class HourseTradeCenter(SellerService):

    def sellerHourse(self):
        print("交易中心审核材料手续")
        print('交易中心签约买房子')
        print('交易中心收买家钱担保给卖家')
        print("交易中心走完流程")


class AgentSellerService(SellerService):

    def __init__(self, name="agent"):
        super(AgentSellerService, self)
        self._name = name
        self._true_service_system = HourseTradeCenter()

    def sellerHourse(self):
        print(f"中介机构{self._name}收取卖家资料，提交中介走流程")
        self._true_service_system.sellerHourse()
        print(f"中介机构{self._name}收取卖家的手续费")
        print("交易结束")



agent = AgentSellerService(name="我爱我家")
agent.sellerHourse()
