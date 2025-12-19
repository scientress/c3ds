from enum import Enum, StrEnum


class DisplayCommands(StrEnum):
    PING = 'ping'
    PONG = 'pong'
    RELOAD = 'reload'
    REMOTE_SHELL_MESSAGE = 'rsMSG'
    REMOTE_SHELL_RESULT = 'rsRES'
    NTP_REQUEST = 'NTPRequest'
    NTP_RESPONSE = 'NTPResponse'