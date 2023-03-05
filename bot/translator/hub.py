from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub, TranslatorRunner


class Translator:
    def __init__(self):
        self.t_hub = TranslatorHub(
            {
                "uk_UA": (
                    "uk_UA",
                    "en_US",
                ),
                "en_US": ("en_US",),
            },
            [
                FluentTranslator(
                    locale="uk_UA",
                    translator=FluentBundle.from_files(
                        "uk_UA", filenames=["locales/ua.ftl"], use_isolating=False
                    ),
                ),
                FluentTranslator(
                    locale="en_US",
                    translator=FluentBundle.from_files(
                        "en_US", filenames=["locales/en.ftl"], use_isolating=False
                    ),
                ),
            ],
            root_locale="uk_UA",
        )

    def __call__(self, language: str) -> TranslatorRunner:
        return self.t_hub.get_translator_by_locale(language)
