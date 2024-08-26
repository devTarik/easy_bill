from src.receipt.models import Receipt, ReceiptProduct
from src.receipt.schemas import PaymentTypeEnum
from src.translations import receipts_text


class ReceiptConstructor:
    def __init__(self, store_name: str, receipt: Receipt, row_length: int = 40, language: str = "uk"):
        self.store_name = store_name
        self.receipt = receipt
        self.row_length = row_length
        self.language = language

    def get_text(self, text: str) -> str:
        texts = receipts_text.get(self.language, {})
        return texts.get(text)

    def separator(self, sep: str = "-", length: int | None = None) -> str:
        row_length = length or self.row_length
        return str(sep * row_length)

    def cut(self, text: str) -> str:
        if len(text) > self.row_length:
            return text[: self.row_length]
        return text

    def align_in_width(self, text_first: str, text_second: str) -> str:
        try:
            string = f"{text_first:<{self.row_length - len(str(text_second))}}{text_second}"
            if len(string) > self.row_length:
                string = f"{self.cut(str(text_first))}\n{self.cut(str(text_second)):>{self.row_length}}"
        except ValueError:
            string = f"{self.cut(str(text_first))}\n{self.cut(str(text_second)):>{self.row_length}}"
        return string

    def align_in_center(self, text: str) -> str:
        if len(text) > self.row_length:
            string = self.cut(text)
        else:
            padding = (self.row_length - len(text)) // 2
            string = f"{' ' * padding}{text}"
        return string

    def row_store_name(self) -> str:
        title = f"{self.get_text('shop')}:"
        string = self.align_in_width(title, self.store_name)
        return string

    def client_name(self) -> str:
        title = f"{self.get_text('buyer')}:"
        username = self.receipt.user.full_name
        string = self.align_in_width(title, username)
        return string

    def get_payment_type(self, payment_type: str) -> str:
        if payment_type == PaymentTypeEnum.CASH.value:
            return self.get_text("cash")
        elif payment_type == PaymentTypeEnum.CARD.value:
            return self.get_text("card")

    def single_product_info(self, product: ReceiptProduct) -> str:
        name = product.product.name
        price = product.product.price
        quantity = product.quantity
        total = product.total

        row_quantity = f"{quantity} x {price}"
        row_name = self.align_in_width(name, total)
        product_row = f"{row_quantity}\n{row_name}"
        return product_row

    def header(self) -> str:
        header = []
        header.append(self.separator("="))
        header.append(self.row_store_name())
        header.append(self.separator("-"))
        header.append(self.client_name())
        header.append(self.separator("="))
        return "\n".join(header)

    def footer(self) -> str:
        footer = []
        datetime = self.receipt.created_at.strftime("%m.%d.%Y, %H:%M")
        footer.append(self.align_in_center(datetime))
        footer.append(self.align_in_center(self.get_text("thanks")))
        return "\n".join(footer)

    def products(self) -> str:
        products_lst = []
        products = self.receipt.products
        payment = self.receipt.payment
        for idx, product in enumerate(products):
            products_lst.append(self.single_product_info(product))
            if idx < len(products) - 1:
                separator_len = self.row_length // 2
                products_lst.append(self.separator("-", separator_len))

        products_lst.append(self.separator("="))
        products_lst.append(self.align_in_width(self.get_text("amount"), self.receipt.total))
        products_lst.append(self.align_in_width(self.get_payment_type(payment.type), payment.amount))
        products_lst.append(self.align_in_width(self.get_text("rest"), payment.rest))
        products_lst.append(self.separator("="))
        return "\n".join(products_lst)

    def create(self) -> str:
        receipt = []
        receipt.append(self.header())
        receipt.append(self.products())
        receipt.append(self.footer())
        return "\n".join(receipt)
