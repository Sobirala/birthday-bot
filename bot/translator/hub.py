from fluent_compiler.bundle import FluentBundle
from fluentogram import FluentTranslator, TranslatorHub, TranslatorRunner

from bot.enums import Language


class Translator:
    def __init__(self) -> None:
        self.t_hub = TranslatorHub(
            {
                Language.UA: (
                    Language.UA,
                    Language.EN,
                ),
                Language.EN: (Language.EN,),
            },
            [
                FluentTranslator(
                    locale=Language.UA,
                    translator=FluentBundle.from_files(
                        Language.UA, filenames=["locales/ua.ftl"], use_isolating=False
                    ),
                ),
                FluentTranslator(
                    locale=Language.EN,
                    translator=FluentBundle.from_files(
                        Language.EN, filenames=["locales/en.ftl"], use_isolating=False
                    ),
                ),
            ],
            root_locale=Language.UA,
        )

    def __call__(self, language: str) -> TranslatorRunner:
        return self.t_hub.get_translator_by_locale(language)
