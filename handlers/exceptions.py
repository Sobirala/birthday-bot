from os import environ
from aiogram import Router, types, F
import logging

router = Router()
router.message.filter(F.chat.type.in_({"private"}))

if environ["DEBUG"] == "1":
    logging.debug("Start DEBUG mode!")


    @router.message(F.chat.func(lambda chat: chat.id != int(environ["ADMIN"])))
    async def test(message: types.Message):
        return await message.answer("Технічні роботи")


@router.message(~F.text)
async def sticker_or_photo(message: types.Message):
    return await message.answer("Я вас не розумію. Надішліть текстове повідомлення будь-ласка.")
