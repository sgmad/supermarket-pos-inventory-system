from dataclasses import dataclass


@dataclass(frozen=True)
class AdminContext:
    admin_account_id: int


@dataclass(frozen=True)
class CashierContext:
    cashier_account_id: int
    register_id: int