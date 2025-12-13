from aiogram import Router, F, types

chat_router = Router()

@chat_router.message(F.text)
async def invoke(message: types.Message):
    if message.text.startswith("/"):
        return
    await message.answer(message.text)