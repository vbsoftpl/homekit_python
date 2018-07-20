#
# Copyright 2018 Joachim Lusiardi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


class HomeKitException(Exception):
    """Generic HomeKit exception.
    Attributes:
        stage: the stage that the exception occurred at
    """

    def __init__(self, stage):
        self.stage = stage

    pass


class HttpException(HomeKitException):
    """
    Used within the HTTP Parser.
    """
    pass


class UnknownError(HomeKitException):
    """
    Raised upon receipt of an unknown error (transmission of kTLVError_Unknown). The spec says that this can happen
    during "Add Pairing" (chapter 4.11 page 51) and "Remove Pairing" (chapter 4.12 page 53).
    """
    pass


class AuthenticationError(HomeKitException):
    """Raised upon receipt of an authentication error"""
    pass


class BackoffError(HomeKitException):
    """Raised upon receipt of a backoff error"""
    pass


class MaxPeersError(HomeKitException):
    """Raised upon receipt of a maxpeers error"""
    pass


class MaxTriesError(HomeKitException):
    """Raised upon receipt of a maxtries error"""
    pass


class UnavailableError(HomeKitException):
    """Raised upon receipt of an unavailable error"""
    pass


class BusyError(HomeKitException):
    """Raised upon receipt of a busy error"""
    pass


class InvalidError(HomeKitException):
    """Raised upon receipt of an error not defined in the HomeKit spec"""
    pass


class IllegalData(HomeKitException):
    """
    # TODO still required?
    Raised upon receipt of invalid encrypted data"""
    pass


class InvalidAuthTagError(HomeKitException):
    """
    Raised upon receipt of an invalid auth tag in Pair Verify Step 3.3 (Page 49).
    """
    pass


class IncorrectPairingIdError(HomeKitException):
    """
    Raised in Pair Verify Step 3.5 (Page 49) if the accessory responds with an unexpected pairing id.
    """
    pass


class InvalidSignatureError(HomeKitException):
    """
    Raised upon receipt of an invalid signature either from an accessory or from the controller.
    """
    pass


class HomeKitStatusException(Exception):
    # TODO really needed?
    def __init__(self, status_code):
        self.status_code = status_code


class ConfigurationError(HomeKitException):
    """
    Used if any configuration in the HomeKit AccessoryServer's context was wrong.
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class FormatError(HomeKitException):
    """
    Used if any format conversion fails or is impossible.
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class CharacteristicPermissionError(HomeKitException):
    """
    Used if the characteristic's permissions do not allow the action. This includes reads on write only characteristics
    and writes on read only characteristics.
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class AccessoryNotFoundError(HomeKitException):
    """
    Used if a HomeKit Accessory's IP and port could not be received via Bonjour / Zeroconf. This might be a temporary
    issue due to the way Bonjour / Zeroconf works.
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class ConfigLoadingError(HomeKitException):
    """
    Used on problems loading some config. This includes but may not be limited to:
     * problems with file permissions (file not readable)
     * the file could not be found
     * the file does not contain parseable JSON
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class ConfigSavingError(HomeKitException):
    """
    Used on problems saving some config. This includes but may not be limited to:
     * problems with file permissions (file not writable)
     * the file could not be found (occurs if the path does not exist)
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class UnpairedError(HomeKitException):
    """
    This should be raised if a paired accessory is expected but the accessory is still unpaired.
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class AlreadyPairedError(HomeKitException):
    """
    This should be raised if an unpaired accessory is expected but the accessory is already paired.
    """
    def __init__(self, message):
        Exception.__init__(self, message)
