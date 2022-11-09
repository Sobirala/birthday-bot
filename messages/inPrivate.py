from jinja2 import Environment
from babel.dates import format_datetime

environment = Environment(trim_blocks=True, enable_async=True)

START = """
Невідома чи неактивна команда 🤔
Список команд та допомога - /help
"""

HELP = """
Про Собіралу
Я допомагаю учасникам колективів не забувати про дні народження один одного.

Як я працюю
1. Додайте мене до групового чату, де потрібно відстежувати дні народження. Ось зручне посилання для цього: t.me/sobiralaDNBot?startgroup=1
Не турбуйтеся, мені не потрібно бути адміністратором у групі, і я не вмію читати листування 🙈

2. Після додавання до групи я запропоную учасникам повідомити дати народження. Вони зможуть це зробити в особистому листуванні зі мною. Вік учасників залишиться у секреті.

3. Дізнавшись дати народження, я почну:
- нагадувати про майбутні ДН потай від іменинників (приватно, в особистих повідомленнях);
- Вітати іменинників у групі.

Переглядати календар днів народження групи та отримувати повідомлення про майбутні ДН можуть лише ті, хто вніс свою дату народження до календаря групи.

Команди у цьому чаті
/calendar — переглянути всі дні народження
/reset - змінити дані про себе
/removeme - видалити дані про себе
/donate - допомогти проекту Собірап

Команди у груповому чаті
/start — Вивести повідомлення з пропозицією додати ДН до календаря групи
/collect — увімкнути чи вимкнути збори грошей (тільки для адміністраторів групи)

Корисні посилання
Допомога та FAQ - url/help
Технічна підтримка - support_bot
Новини проекту - @KulunchickDev
"""

ADD = environment.from_string("""
Вітання! Давайте додамо вашу дату народження до календаря групи <b>«{{ groupname }}»</b>.
""")

YEAR = """
Почнемо з року народження - надішліть мені 4 цифри. Ця інформація тільки для мене, і я нікому не повідомлю ваш вік 🤐
"""

NOT_YEAR = """
Не схоже на рік. Спробуйте ввести 4 цифри. Наприклад: 2005.
"""

MONTH = """
Добре. Оберіть місяць народження, будь ласка.
"""

NOT_MONTH = """
Не схоже на місяць. Виберіть опцію на спеціальній клавіатурі або надішліть назву місяця текстом, без скорочень.
"""

DAY = """
Зрозумів. Тепер введіть день народження.
"""

NOT_DAY = """
Не схоже на день. Спробуйте ще раз – мені потрібна одна чи дві цифри. приклад: 19.
"""

GENDER = """
Вкажіть вашу стать, щоб я міг грамотно звертатися до вас.
"""

NOT_GENDER = """
Будь ласка, виберіть опцію на спеціальній клавіатурі або надішліть мені "Ч" або "Ж".
"""

SUCCESS_USER = environment.from_string("""
Ви народилися {{ birthday }}. Ваша стать — {{ gender }}. Все вірно?
""")

NOT_SUCCESS_USER = """
Почнемо спочатку. В якому році Ви народились? Надішліть мені 4 цифри.
"""

TOWN = """
Чудово! Останнє питання. Для коректної роботи мені важливо розуміти, в якій тимчасовій зоні ви знаходитесь. Надішліть мені назву вашого міста.
"""

SUCCESS_TOWN = environment.from_string("""
Ви знаходитесь в «{{ address }}». У вас зараз {{ date }} та {{ time }}. Все вірно?
""")

NOT_TOWN = """
Не розумію, що то за місто. Спробуйте так: "Київ, Україна".
"""

NOT_SUCCESS_TOWN = """
Нічого спробуємо ще раз. Надішліть мені назву вашого міста та країну. Приклад: Крим, Україна.
"""

RESET = """
⚠️⚠️⚠️ Будьте уважні, у вас є лише одна спроба змінити дані.

Наступного разу зможете змінити дані лише за кілька місяців.

Ви впевнені, що хочете змінити дані про себе (дата народження, стать, годинна зона)? Якщо ні, просто проігноруйте це повідомлення.
"""

NOT_SUCCESS = """
Не зрозумів вас. Будь ласка, виберіть опцію на спеціальній клавіатурі або надішліть мені "Так" або "Ні".
"""

SUCCESS_ADD = environment.from_string("""
✔️ Ваш день народження внесено до календаря групи «{{ groupname }}»!
За командою /calendar ви можете побачити усі дні народження групи.

Тепер я буду:
— приватно нагадувати вам про найближчі дні народження 🔔
— запрошувати вас до секретних чатів для обговорення найближчих ДН 🤫
— вітати іменинників у групі о 9 ранку за їхньою тимчасовою зоною 🥳
{% if is_admin %}
— повідомляти про деякі інші події, оскільки ви адмін у групі 😎
{% endif %}

Підписуйтесь на канал @KulunchickDev, щоб стежити за оновленнями бота.
""")

YET_ADD = environment.from_string("""
Вашу дату народження вже внесено до календаря групи «{{ groupname }}». Жодних дій не потрібно.
""")

CALENDAR = environment.from_string("""
🗓 Дні народження учасників гурту «<b>{{ groupname }}<b>» та їх годинникові зони:
{% for month in group %}

<b>{{ month._id.month_str }}</b>
{% for user in month["users"] %}
<a href="tg://user?id={{ user._id }}">{{ user.username }}</a>, {{ format_datetime(user.birthday, "d MMMM", locale="uk_UA") }} [{{ user.timezone }}]
{% endfor %}
{% endfor %}
""")
CALENDAR.globals.update(format_datetime=format_datetime)
