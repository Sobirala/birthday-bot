from jinja2 import Environment
from babel.dates import format_datetime

environment = Environment(trim_blocks=True, enable_async=True)

environment.globals.update(format_datetime=format_datetime)

TOMORROW = environment.from_string("""

""")

NEXT_5_DAY = environment.from_string("""
🔔 {{ format_datetime(user.birthday, "d MMMM", locale="uk_UA") }}, через 5 днів, день народження у {{ user.fullname }} ({{ group.name }}).
""")
