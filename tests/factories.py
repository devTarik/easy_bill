from factory import Factory, Faker, List, SubFactory

from src.receipt.schemas import PaymentSchema, PaymentTypeEnum, ProductSchema, ReceiptRequestSchema


class ProductFactory(Factory):
    name = Faker("word")
    price = Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    quantity = Faker("pydecimal", left_digits=1, right_digits=1, positive=True)

    class Meta:
        model = ProductSchema


class PaymentFactory(Factory):
    class Meta:
        model = PaymentSchema

    type = PaymentTypeEnum.CASH
    amount = Faker("pydecimal", left_digits=3, right_digits=2, positive=True)


class ReceiptFactory(Factory):
    class Meta:
        model = ReceiptRequestSchema

    products = List([SubFactory(ProductFactory) for _ in range(3)])
    payment = SubFactory(PaymentFactory)
