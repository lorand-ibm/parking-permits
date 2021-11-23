class PermitLimitExceeded(Exception):
    pass


class PriceError(Exception):
    pass


class InvalidUserZone(Exception):
    pass


class InvalidContractType(Exception):
    pass


class NonDraftPermitUpdateError(Exception):
    pass


class PermitCanNotBeDelete(Exception):
    pass


class PermitCanNotBeEnded(Exception):
    pass


class RefundCanNotBeCreated(Exception):
    pass
