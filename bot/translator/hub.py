from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub, TranslatorRunner


class Translator:
    def __init__(self):
        self.t_hub = TranslatorHub(
            {
                "uk-UA": (
                    "uk-UA",
                    "en-US",
                ),
                "en-US": ("en-US",),
            },
            [
                FluentTranslator(
                    locale="uk-UA",
                    translator=FluentBundle.from_files(
                        "uk-UA", filenames=["../locales/ua.ftl"], use_isolating=False
                    ),
                ),
                FluentTranslator(
                    locale="en-US",
                    translator=FluentBundle.from_files(
                        "en-US", filenames=["../locales/en.ftl"], use_isolating=False
                    ),
                ),
            ],
            root_locale="uk-UA",
        )

    def __call__(self, language: str) -> TranslatorRunner:
        return self.t_hub.get_translator_by_locale(language)
