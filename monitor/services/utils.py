import typing as t


# some strange ISO format with Z in the end, that datetime
# can't parse, so just cut it off
def gnosis_date_to_iso(date: str) -> str:
    dot_position = date.find('.')

    return date[:dot_position]
