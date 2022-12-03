from aiogram import Router, types, F

router = Router()
router.message.filter(F.chat.type.in_({"private"}))


@router.message(~F.text)
async def sticker_or_photo(message: types.Message):
    return await message.answer("Я вас не розумію. Надішліть текстове повідомлення будь-ласка.")
