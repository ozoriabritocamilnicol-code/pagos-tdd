class OrderNotFoundError(Exception):
    pass


class PaymentService:
    def __init__(self, gateway, repository, notifier):
        pass

    def pay(self, order_id):
        pass