# -*- coding: utf-8 -*-


class RoboError(Exception):
    pass


class InvalidNameError(RoboError):
    pass


class InvalidSubmitError(RoboError):
    pass
