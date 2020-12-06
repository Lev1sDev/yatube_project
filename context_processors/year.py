import datetime as dt


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    this_year = dt.datetime.today().year
    return {
        "year": this_year
    }
