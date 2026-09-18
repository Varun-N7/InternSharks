from datetime import date


company_holidays = [
    {
        "date": "2026-10-02",
        "name": "Gandhi Jayanti",
    },
    {
        "date": "2026-10-20",
        "name": "Company Holiday",
    },
]


def get_company_holidays(start_date=None, end_date=None):
    holidays = company_holidays

    if start_date:
        try:
            start = date.fromisoformat(start_date)
        except ValueError:
            raise ValueError("Invalid start date")

        holidays = [
            holiday
            for holiday in holidays
            if date.fromisoformat(holiday["date"]) >= start
        ]

    if end_date:
        try:
            end = date.fromisoformat(end_date)
        except ValueError:
            raise ValueError("Invalid end date")

        holidays = [
            holiday
            for holiday in holidays
            if date.fromisoformat(holiday["date"]) <= end
        ]

    return holidays