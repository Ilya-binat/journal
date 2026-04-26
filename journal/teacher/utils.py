from datetime import date, timedelta

def get_week_days():
    today = date.today()

    # находим понедельник текущей недели
    monday = today - timedelta(days=today.weekday())

    week_days = []

    for i in range(6):  # Пн–Сб (6 дней)
        day_date = monday + timedelta(days=i)

        week_days.append({
            "date": day_date,
            "day": day_date.day,
            "month": day_date.strftime("%b"),  # или "%B" для полного названия
            "weekday": day_date.strftime("%a"),  # Mon, Tue...
            "is_today": day_date == today
        })

    return week_days