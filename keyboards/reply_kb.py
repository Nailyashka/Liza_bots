from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

start_kb = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton(text='Меню'), KeyboardButton(text='О магазине')],
        [KeyboardButton(text='Варианты доставки'), KeyboardButton(text='Варианты оплаты')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Что вас интересует?'
)

del_kb = ReplyKeyboardRemove()


async def kb2():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(
        KeyboardButton(text='Меню'), 
        KeyboardButton(text='О магазине'),
        KeyboardButton(text='Варианты доставки'),
        KeyboardButton(text='Варианты оплаты'),
    )
    return keyboard.adjust(2,2)
    # return keyboard.as_markup(resize_keyboard=True, input_field_placeholder="Что вас интересует?")
    
async def kb3():
    kb2_builder = await kb2()
    kb2_builder.add(KeyboardButton(text='Отзывы'))
    keyboard_markup_3 = kb2_builder.adjust(2,2,1).as_markup(resize_markup = True, input_field_placeholder='Что вас интересует?')
    return keyboard_markup_3

def get_keyboard(
    *btns: str,
    placeholder: str = None,
    request_contact: int = None,
    request_location: int = None,
    sizes: tuple[int] = (2,),
):
    '''
    Parameters request_contact and request_location must be as indexes of btns args for buttons you need.
    Example:
    get_keyboard(
            "Меню",
            "О магазине",
            "Варианты оплаты",
            "Варианты доставки",
            "Отправить номер телефона"
            placeholder="Что вас интересует?",
            request_contact=4,
            sizes=(2, 2, 1)
        )
    '''
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):
        
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))

        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:

            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(
            resize_keyboard=True, input_field_placeholder=placeholder)






# start_kb2 = ReplyKeyboardBuilder()
# start_kb2.add(
#     KeyboardButton(text='Меню'), 
#     KeyboardButton(text='О магазине'),
#     KeyboardButton(text='Варианты доставки'),
#     KeyboardButton(text='Варианты оплаты'),
# ).adjust(2,2)

# start_kb3.attach(start_kb2).row(KeyboardButton(text='Оставьте отзыв'))

