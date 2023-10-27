from datetime import date, datetime


# ---------------> to mock  <-----------------
# import model.commons.time
# from model.commons.time import current_date

# model.commons.time.current_datetime = lambda: datetime(2020,12,1,2,2,2)


def current_datetime() -> datetime:
    return datetime.utcnow()


def current_date() -> date:
    return current_datetime().date()
