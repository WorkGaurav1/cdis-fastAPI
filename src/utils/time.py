# Shared "naive but UTC-by-convention" timestamp helper.
#
# MySQL's DATETIME column has no timezone concept, so a tz-aware value
# round-trips through the DB as naive anyway -- storing (and later
# comparing) naive UTC consistently avoids Python raising on
# aware-vs-naive datetime comparisons once a value comes back out of
# the database.

from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
