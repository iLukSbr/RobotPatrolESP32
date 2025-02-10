import time
import sys
from .constants import ENABLE_INFO_PRINT, ENABLE_ERROR_PRINT

def format_iso_datetime(timestamp):
    """
    Formata um timestamp em uma string ISO 8601.
    
    :param timestamp: Uma tupla contendo ano, mês, dia, hora, minuto, segundo.
    :return: Uma string formatada no padrão ISO 8601.
    """
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(
        timestamp[0], timestamp[1], timestamp[2], timestamp[4], timestamp[5], timestamp[6]
    )

def format_brt_datetime(timestamp, weekday):
    """
    Formata um timestamp em uma string brasileira.
    
    :param timestamp: Uma tupla contendo ano, mês, dia, hora, minuto, segundo, dia da semana.
    :return: Uma string formatada no padrão brasileiro.
    """
    return "{:s}, {:02d}/{:02d}/{:04d} {:02d}:{:02d}:{:02d} {:s}".format(weekday, timestamp[2], timestamp[1], timestamp[0], timestamp[4], timestamp[5], timestamp[6], "BRT")

def info_print(message):
    if ENABLE_INFO_PRINT:
        print(f"INFO: {message}")

def error_print(message):
    if ENABLE_ERROR_PRINT:
        print(f"ERROR: {message}", file=sys.stderr)
