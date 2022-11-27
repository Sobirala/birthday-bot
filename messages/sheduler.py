from jinja2 import Environment
from babel.dates import format_datetime

environment = Environment(trim_blocks=True, enable_async=True)

environment.globals.update(format_datetime=format_datetime)

TOMORROW = environment.from_string("""
🔔 Завтра, {{ format_datetime(user.birthday, "d MMMM", locale="uk_UA") }}, день народження <a href="tg://user?id={{ user._id }}">{{ user.fullname }}</a> ({{ title }}). Не забудьте привітати!
""")

NEXT_5_DAY = environment.from_string("""
🔔 {{ format_datetime(user.birthday, "d MMMM", locale="uk_UA") }}, через 5 днів, день народження у <a href="tg://user?id={{ user._id }}">{{ user.fullname }}</a> ({{ title }}).
""")
