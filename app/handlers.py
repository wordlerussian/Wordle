import random,os,asyncio
from aiogram import F,Router
from aiogram.filters import CommandStart,Command
from aiogram.types import Message,CallbackQuery,FSInputFile
import app.keyboard as kb
from aiogram.fsm.state import State,StatesGroup
from aiogram.enums.message_entity_type import MessageEntityType
from dotenv import load_dotenv
from openai import OpenAI
from app.database.database import async_session
from app.database.models import Game
from sqlalchemy import select
load_dotenv()
router = Router()

def generate():
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("AITOKEN"),
    )

    completion = client.chat.completions.create(
    extra_headers={},
    extra_body={},
    model="deepseek/deepseek-chat-v3-0324",
    messages=[
        {
        "role": "user",
        "content": "Ответь одним рандомным русским словом из 5 букв,только слово больше НИЧЕГО НИ СКОБКИ НИ ЭМОДЗИ ПРОСТО СЛОВО ИМЕННО ИЗ 5 БУКВ"
        }
    ]
    )
    ans = completion.choices[0].message.content
    if len(ans) != 5:
        return generate()
    return ans.lower()

def ask(a):
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("AITOKEN"),
    )
    completion = client.chat.completions.create(
    extra_headers={},
    extra_body={},
    model="deepseek/deepseek-chat-v3-0324",
    messages=[
        {
        "role": "user",
        "content": f"ОТВЕТЬ ОДНИМ СЛОВОМ.ЕСЛИ ЭТО СЛОВО - {a} ЕСТЬ В РУССКОМ ЯЗЫКЕ НАПИШИ True,иначе False ПРОСТО True или False !!!,ПРИМЕР мегарище -> False,кошка -> True"
        }
    ]
    )
    ans = completion.choices[0].message.content
    if ans == "True":
        return True
    elif ans == 'False':
        return False
    else : 
        return ask(a)

@router.message(CommandStart())
async def start(message : Message):
    await message.reply(f"<b>Добро пожаловать в игру про Wordle, {message.from_user.first_name} !\nЧтобы начать играть можете просто нажать на кнопку снизу сообщения ⤵️</b>\nПравила игры в Wordle:\nПосле нажатия на кнопку играть, бот выберет одно слово состоящие из 5 букв. Вам надо будет угадать какое же это слово.\nЧтобы угадать вы должны скидывать реальные слова из 5 букв, а бот скажет какие буквы подходят, а какие нет. Вот что означают все символы от бота :\n🟥 -> Означает что этой буквы вообще нету в слове\n🟨 -> Означает что эта буква есть в слове но она в другом месте\n🟩 -> Означает что и буква и расположение верны\nИгра закончиться тогда когда вы найдете все 5 букв\nУдачи игроки 🍀",reply_markup=kb.main2,parse_mode="HTML")
    await message.answer(f"На данный момент у вас есть 6 попыток угадать слово,но вы можете изменить его на бесконечность с помощью настроек снизу ⤵️",reply_markup=kb.main3)
    async with async_session() as session:
        game = await session.get(Game, message.from_user.id)
        if not game:
            game = Game(
                user_id = message.from_user.id,
                word = "",
                lifes = 6,
                infinity = False,
                is_playing = False
            )
        session.add(game)
        await session.commit()

@router.message(F.text == "my_id")
async def my_id(message : Message):
    await message.reply(f"Ваш id : {message.from_user.id}")

@router.message(Command("settings"))
async def settings1(message : Message):
    await message.delete()
    async with async_session() as session:
        game = await session.get(Game,message.from_user.id)
        if game:
            if game.is_playing:
                await message.answer("На данный момент вы играете, желаете выйти из игры чтобы зайти в настройки ?",reply_markup=kb.main7)
            else:
                if game.infinity:
                    await message.answer("На данный момент у вас включена опция бесконечных жизней, желаете выключить ее ?",reply_markup=kb.main4) 
                else:
                    await message.answer("На данный момент у вас 6 жизней,но вы можете изменить его на бесконечность, желаете изменить ?",reply_markup=kb.main5)

@router.callback_query(F.data == "start_play")
async def start_play(callback : CallbackQuery):
    await callback.answer("")
    msg = await callback.message.answer("Ждем чтобы AI сделал слово... 🤖")
    word = await asyncio.to_thread(generate)
    await msg.edit_text("Игра началась ! 🎰\nМожете скидывать слова !")
    async with async_session() as session:
        game = await session.get(Game, callback.from_user.id)
        if not game:
            game = Game(user_id=callback.from_user.id, word=word, lifes=6, infinity=False, is_playing=True)
            session.add(game)
        else:
            game.word = word
            game.is_playing = True
            if not game.infinity:
                game.lifes = 6
        await session.commit()

@router.message(F.text)
async def play(message : Message):
    if message.text.startswith("/"):
        return
    async with async_session() as session:
        game = await session.get(Game, message.from_user.id)

        if not game.is_playing or not game:
            return

        t = message.text.lower()
        if len(t) != 5:
            await message.reply("Это слово не подходит ❌\nОно должно состоять из 5 букв !",reply_markup=kb.main6)
            return

        if t == game.word:
            await message.answer("Отличная работа, ты угадал слово ! ✅\nЕсли хочешь играть еще нажми на кнопку ниже ⤵️",reply_markup=kb.main2)
            game.is_playing = False
            await session.commit()
            return
        
        ans = ["🟥"] * 5
        used = [False] * 5
        for i in range(5):
            if t[i] == game.word[i]:
                ans[i] = "🟩"
                used[i] = True
        for i in range(5):
            if ans[i] == "🟩":
                continue
            for j in range(5):
                if not used[j] and t[i] == game.word[j]:
                    ans[i] = "🟨"
                    used[j] = True
                    break
        res = "".join(ans)

        if not game.infinity:
            game.lifes -= 1
            if game.lifes <= 0:
                await message.answer(f"Твои жизни закончились, ты проиграл !\nЗагаданное слово : {game.word}",reply_markup=kb.main2)
                game.is_playing = False
            else:
                await message.answer(f"Немножко не повезло !\nТвое слово: {res}\nОсталось жизней : {game.lifes}",reply_markup=kb.main6)
        else:
            await message.answer(f"Немножко не повезло !\nТвое слово: {res}",reply_markup=kb.main6)

        await session.commit()
    
@router.callback_query(F.data == "settings")
async def settings(callback : CallbackQuery):
    await callback.answer("")
    async with async_session() as session:
        game = await session.get(Game,callback.from_user.id)
        if game and game.infinity:
            await callback.message.answer("На данный момент у вас включена опция бесконечных жизней, желаете выключить ее ?",reply_markup=kb.main4) 
        else:
            await callback.message.answer("На данный момент у вас 6 жизней,но вы можете изменить его на бесконечность, желаете изменить ?",reply_markup=kb.main5)

@router.callback_query(F.data == "nothing")
async def nothing(callback : CallbackQuery):
    await callback.answer("")
    await callback.message.delete()

@router.callback_query(F.data == "turn_on_inf")
async def turn_on_inf(callback : CallbackQuery):
    await callback.answer("")
    async with async_session() as session:
        game = await session.get(Game,callback.from_user.id)
        game.infinity = True
        await session.commit()
    await callback.message.delete()
    await callback.message.answer("Теперь у вас бесконечные жизни ! ♾️",reply_markup=kb.main2)

@router.callback_query(F.data == "turn_off_inf")
async def turn_off_inf(callback : CallbackQuery):
    await callback.answer("")
    async with async_session() as session:
        game = await session.get(Game,callback.from_user.id)
        game.infinity = False
        await session.commit()
    await callback.message.delete()
    await callback.message.answer("Теперь у вас 6 жизней !",reply_markup=kb.main2)

@router.callback_query(F.data == "quit")
async def quit(callback : CallbackQuery):
    await callback.answer("")
    async with async_session() as session:
        game = await session.get(Game,callback.from_user.id)
        if game:
            if not game.is_playing:
                await callback.message.reply("На данный момент вы не играете ❌")
                return
            game.is_playing = False
            await callback.message.answer(f"Игра закончилась, ранее загаданное слово -> {game.word}",reply_markup=kb.main2)
        await session.commit()

@router.callback_query(F.data == "settings_yes")
async def settings_yes(callback : CallbackQuery):
    await callback.answer()
    await callback.message.delete()
    async with async_session() as session:
        game = await session.get(Game,callback.from_user.id)
        if game:
            game.is_playing = False
            await callback.message.answer(f"Игра закончилась, ранее загаданное слово -> {game.word}",reply_markup=kb.main2)
            if game.infinity:
                await callback.message.answer("На данный момент у вас включена опция бесконечных жизней, желаете выключить ее ?",reply_markup=kb.main4) 
            else:
                await callback.message.answer("На данный момент у вас 6 жизней,но вы можете изменить его на бесконечность, желаете изменить ?",reply_markup=kb.main5)
        await session.commit()