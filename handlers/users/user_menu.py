# - *- coding: utf- 8 - *-
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery

from keyboards.default import check_user_out_func, all_back_to_main_default
from keyboards.inline import *
from keyboards.inline.inline_page import *
from loader import dp, bot
from states.state_users import *
from utils.other_func import clear_firstname, get_dates
from data.config import admin_for_logs

# Разбив сообщения на несколько, чтобы не прилетало ограничение от ТГ
def split_messages(get_list, count):
    return [get_list[i:i + count] for i in range(0, len(get_list), count)]


#####################ДОБАВЛЯЕМ КНОПКИ#################################

### РЕФЕРАЛКА ###

@dp.message_handler(text="🎁 Реферальная система", state="*")
async def bot_start(message: types.Message, state: FSMContext):
    with open("ref.jpg", "rb") as file: #Тут_вставить_название_картинки_для_рефки
        data = file.read()
        me = await bot.get_me()
        clear_address = InlineKeyboardMarkup()
        clear_address.add(InlineKeyboardButton(text="Скрыть", callback_data="close"))
    await message.answer_photo(photo=data, caption=f"<b><i>💙 Реферальная система 💙\n\n"
                        f"🔗 Ссылка: \n"
                        f"<code>https://t.me/{me.username}?start={message.from_user.id}</code>\n\n"
                        f"📘 Наша реферальная система позволит вам заработать крупную сумму без вложений. Вам необходимо лишь давать свою ссылку друзьям и вы будете получать пожизненно 2% с их пополнений в боте</i></b>", reply_markup=clear_address)


@dp.callback_query_handler(text='close')
async def get_my_address(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

### ###

#################################

# Обработка кнопки "Купить"
@dp.message_handler(text="🛍 Товары", state="*")
async def show_search(message: types.Message, state: FSMContext):
    await state.finish()
    get_categories = get_all_categoriesx()
    if len(get_categories) >= 1:
        get_kb = buy_item_open_category_ap(0)
        await message.answer("<b>🤔 Выберите необходимую категорию:</b>", reply_markup=get_kb)
    else:
        await message.answer("<b>😥 Товары в данной категории временно отсутствует.</b>")


# Обработка кнопки "Профиль"
@dp.message_handler(text="👮🏻‍♀️ Профиль", state="*")
async def show_profile(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(get_user_profile(message.from_user.id), reply_markup=open_profile_inl)


# Обработка кнопки "FAQ"
@dp.message_handler(text="📕 Правила", state="*")
async def show_my_deals(message: types.Message, state: FSMContext):
    await state.finish()
    get_settings = get_settingsx()
    send_msg = get_settings[1]
    if "{username}" in send_msg:
        send_msg = send_msg.replace("{username}", f"<b>{message.from_user.username}</b>")
    if "{user_id}" in send_msg:
        send_msg = send_msg.replace("{user_id}", f"<b>{message.from_user.id}</b>")
    if "{firstname}" in send_msg:
        send_msg = send_msg.replace("{firstname}", f"<b>{clear_firstname(message.from_user.first_name)}</b>")
    clear_address = InlineKeyboardMarkup()
    clear_address.add(InlineKeyboardButton(text="Закрыть", callback_data="close"))
    await message.answer(send_msg, disable_web_page_preview=True, reply_markup=clear_address)

@dp.callback_query_handler(text='close')
async def get_my_address(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

# Обработка кнопки "Поддержка"
@dp.message_handler(text="☎️ Поддержка", state="*")
async def show_contact(message: types.Message, state: FSMContext):
    await state.finish()
    get_settings = get_settingsx()
    clear_address = InlineKeyboardMarkup()
    clear_address.add(InlineKeyboardButton(text="Закрыть", callback_data="close"))
    await message.answer(get_settings[0], disable_web_page_preview=True, reply_markup=clear_address)

@dp.callback_query_handler(text='close')
async def get_my_address(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

# Обработка колбэка "Мои покупки"
@dp.callback_query_handler(text="my_buy", state="*")
async def show_referral(call: CallbackQuery, state: FSMContext):
    last_purchases = last_purchasesx(call.from_user.id)
    if len(last_purchases) >= 1:
        await call.message.delete()
        count_split = 0
        save_purchases = []
        for purchases in last_purchases:
            save_purchases.append(f"<b>📃 Чек:</b> <code>#{purchases[4]}</code>\n"
                                  f"▶ {purchases[9]} | {purchases[5]}шт | {purchases[6]}руб\n"
                                  f"🕜 {purchases[13]}\n"
                                  f"<code>{purchases[10]}</code>")
        await call.message.answer("<b>🛒 Последние 10 покупок</b>\n"
                                  "➖➖➖➖➖➖➖➖➖➖➖➖➖")
        save_purchases.reverse()
        len_purchases = len(save_purchases)
        if len_purchases > 4:
            count_split = round(len_purchases / 4)
            count_split = len_purchases // count_split
        if count_split > 1:
            get_message = split_messages(save_purchases, count_split)
            for msg in get_message:
                send_message = "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n".join(msg)
                await call.message.answer(send_message)
        else:
            send_message = "\n➖➖➖➖➖➖➖➖➖➖➖➖➖\n".join(save_purchases)
            await call.message.answer(send_message)

        await call.message.answer(get_user_profile(call.from_user.id), reply_markup=open_profile_inl)
    else:
        await call.answer("❗ У вас отсутствуют покупки")


################################################################################################
######################################### ПОКУПКА ТОВАРА #######################################
# Открытие категории для покупки
@dp.callback_query_handler(text_startswith="buy_open_category", state="*")
async def open_category_for_buy_item(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.split(":")[1])
    get_category = get_categoryx("*", category_id=category_id)
    get_positions = get_positionsx("*", category_id=category_id)

    get_kb = buy_item_item_position_ap(0, category_id)
    if len(get_positions) >= 1:
        await call.message.edit_text("<b>🤗 Выбери необходимый товар:</b>",
                                     reply_markup=get_kb)
    else:
        await call.answer(f"❕ Товары в категории {get_category[2]} отсутствуют.")


# Вернутсья к предыдущей категории при покупке
@dp.callback_query_handler(text_startswith="back_buy_item_to_category", state="*")
async def back_category_for_buy_item(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("<b>🤔 Выбери необходимую категорию:</b>",
                                 reply_markup=buy_item_open_category_ap(0))


# Следующая страница категорий при покупке
@dp.callback_query_handler(text_startswith="buy_category_nextp", state="*")
async def buy_item_next_page_category(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>🤗 Выбери необходимый товар:</b>",
                                 reply_markup=buy_item_next_page_category_ap(remover))


# Предыдущая страница категорий при покупке
@dp.callback_query_handler(text_startswith="buy_category_prevp", state="*")
async def buy_item_prev_page_category(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])

    await call.message.edit_text("<b>🤓 Выбери необходимый товар:</b>",
                                 reply_markup=buy_item_previous_page_category_ap(remover))


# Следующая страница позиций при покупке
@dp.callback_query_handler(text_startswith="buy_position_nextp", state="*")
async def buy_item_next_page_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    await call.message.edit_text("<b>☺️ Выбери необходимый товар:</b>",
                                 reply_markup=item_buy_next_page_position_ap(remover, category_id))


# Предыдущая страница позиций при покупке
@dp.callback_query_handler(text_startswith="buy_position_prevp", state="*")
async def buy_item_prev_page_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    await call.message.edit_text("<b>🤗 Выбери необходимый товар:</b>",
                                 reply_markup=item_buy_previous_page_position_ap(remover, category_id))


# Возвращение к страницам позиций при покупке товара
@dp.callback_query_handler(text_startswith="back_buy_item_position", state="*")
async def buy_item_next_page_position(call: CallbackQuery, state: FSMContext):
    remover = int(call.data.split(":")[1])
    category_id = int(call.data.split(":")[2])

    await call.message.delete()
    await call.message.answer("<b>🤗 Выбери необходимый товар:</b>",
                              reply_markup=buy_item_item_position_ap(remover, category_id))


# Открытие позиции для покупки
@dp.callback_query_handler(text_startswith="buy_open_position", state="*")
async def open_category_for_create_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    remover = int(call.data.split(":")[2])
    category_id = int(call.data.split(":")[3])

    get_position = get_positionx("*", position_id=position_id)
    get_category = get_categoryx("*", category_id=category_id)
    get_items = get_itemsx("*", position_id=position_id)

    send_msg = f"<b>🧾 Покупка товара:</b>\n" \
               f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n" \
               f"<b>📜 Категория:</b> <code>{get_category[2]}</code>\n\n" \
               f"<b>🏷 Название:</b> <code>{get_position[2]}</code>\n" \
               f"<b>💵 Стоимость:</b> <code>{get_position[3]}руб</code>\n" \
               f"<b>📦 Количество:</b> <code>{len(get_items)}шт</code>\n\n" \
               f"<b>📜 Описание:</b>\n" \
               f"{get_position[4]}\n"
    if len(get_position[5]) >= 5:
        await call.message.delete()
        await call.message.answer_photo(get_position[5],
                                        send_msg,
                                        reply_markup=open_item_func(position_id, remover, category_id))
    else:
        await call.message.edit_text(send_msg,
                                     reply_markup=open_item_func(position_id, remover, category_id))


# Выбор кол-ва товаров для покупки
@dp.callback_query_handler(text_startswith="buy_this_item", state="*")
async def open_category_for_create_position(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])

    get_items = get_itemsx("*", position_id=position_id)
    get_position = get_positionx("*", position_id=position_id)
    get_user = get_userx(user_id=call.from_user.id)
    if len(get_items) >= 1:
        if int(get_user[4]) >= int(get_position[3]):
            async with state.proxy() as data:
                data["here_cache_position_id"] = position_id
            await call.message.delete()
            await StorageUsers.here_input_count_buy_item.set()
            await call.message.answer(f"📦 <b>Введите количество товаров для покупки</b>\n"
                                      f"▶ От <code>1</code> до <code>{len(get_items)}</code>\n"
                                      f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                      f"🏷 Название товара: <code>{get_position[2]}</code>\n"
                                      f"💵 Стоимость товара: <code>{get_position[3]}руб</code>\n"
                                      f"💳 Ваш баланс: <code>{get_user[4]}руб</code>\n",
                                      reply_markup=all_back_to_main_default)
        else:
            await call.answer("❗ У вас недостаточно средств. Пополните баланс")
    else:
        await call.answer("😳 Товаров нет в наличии.")


# Принятие кол-ва товаров для покупки
@dp.message_handler(state=StorageUsers.here_input_count_buy_item)
async def input_buy_count_item(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        position_id = data["here_cache_position_id"]
    get_items = get_itemsx("*", position_id=position_id)
    get_position = get_positionx("*", position_id=position_id)
    get_user = get_userx(user_id=message.from_user.id)

    if message.text.isdigit():
        get_count = int(message.text)
        amount_pay = int(get_position[3]) * get_count
        if len(get_items) >= 1:
            if 1 <= get_count <= len(get_items):
                if int(get_user[4]) >= amount_pay:
                    await state.finish()
                    delete_msg = await message.answer("<b>💙 Товары подготовлены.</b>",
                                                      reply_markup=check_user_out_func(message.from_user.id))

                    await message.answer(f"<b>💙 Вы действительно хотите купить товар(ы)?</b>\n"
                                         f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                         f"🏷 Название товара: <code>{get_position[2]}</code>\n"
                                         f"💵 Стоимость товара: <code>{get_position[3]}руб</code>\n"
                                         f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                         f"▶ Количество товаров: <code>{get_count}шт</code>\n"
                                         f"💰 Сумма к покупке: <code>{amount_pay}руб</code>",
                                         reply_markup=confirm_buy_items(position_id, get_count,
                                                                        delete_msg.message_id))
                else:
                    await message.answer(f"<b>❌ Недостаточно средств на счете.</b>\n"
                                         f"<b>📦 Введите количество товаров для покупки</b>\n"
                                         f"▶ От <code>1</code> до <code>{len(get_items)}</code>\n"
                                         f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                         f"💳 Ваш баланс: <code>{get_user[4]}</code>\n"
                                         f"🏷 Название товара: <code>{get_position[2]}</code>\n"
                                         f"💵 Стоимость товара: <code>{get_position[3]}руб</code>\n",
                                         reply_markup=all_back_to_main_default)
            else:
                await message.answer(f"<b>❌ Неверное количество товаров.</b>\n"
                                     f"<b>📦 Введите количество товаров для покупки</b>\n"
                                     f"▶ От <code>1</code> до <code>{len(get_items)}</code>\n"
                                     f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                     f"💳 Ваш баланс: <code>{get_user[4]}</code>\n"
                                     f"🏷 Название товара: <code>{get_position[2]}</code>\n"
                                     f"💵 Стоимость товара: <code>{get_position[3]}руб</code>\n",
                                     reply_markup=all_back_to_main_default)
        else:
            await state.finish()
            await message.answer("<b>💙 Товар который вы хотели купить, закончился</b>",
                                 reply_markup=check_user_out_func(message.from_user.id))
    else:
        await message.answer(f"<b>❌ Данные были введены неверно.</b>\n"
                             f"<b>📦 Введите количество товаров для покупки</b>\n"
                             f"▶ От <code>1</code> до <code>{len(get_items)}</code>\n"
                             f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                             f"💳 Ваш баланс: <code>{get_user[4]}</code>\n"
                             f"🏷 Название товара: <code>{get_position[2]}</code>\n"
                             f"💵 Стоимость товара: <code>{get_position[3]}руб</code>\n",
                             reply_markup=all_back_to_main_default)


# Отмена покупки товара
@dp.callback_query_handler(text_startswith="not_buy_items", state="*")
async def not_buy_this_item(call: CallbackQuery, state: FSMContext):
    message_id = call.data.split(":")[1]
    await call.message.delete()
    await bot.delete_message(call.message.chat.id, message_id)
    await call.message.answer("<b>✔️ Вы отменили покупку товаров.</b>",
                              reply_markup=check_user_out_func(call.from_user.id))


# Согласие на покупку товара
@dp.callback_query_handler(text_startswith="xbuy_item:", state="*")
async def yes_buy_this_item(call: CallbackQuery, state: FSMContext):
    position_id = int(call.data.split(":")[1])
    get_position = get_positionx("*", position_id=position_id)
    get_count = int(call.data.split(":")[2])
    amount_pay = int(get_position[3]) * get_count
    random_number = [random.randint(100000000, 999999999)]
    passwd = list("ABCDEFGHIGKLMNOPQRSTUVYXWZ")
    random.shuffle(passwd)
    random_char = "".join([random.choice(passwd) for x in range(1)])
    receipt = random_char + str(random_number[0])
    get_settings = get_settingsx()
    get_items = get_itemsx("*", position_id=position_id)
    get_user = get_userx(user_id=call.from_user.id)
    await bot.send_message(admin_for_logs,text = f'<b>👤 Покупатель: <a href="tg://user?id={get_user[1]}">{get_user[3]}</a> <code>({get_user[1]})</code>\n \n\nКупил товар из категории:</b>\n➖ <code>{get_position[2]}</code>\n<b>В кол-ве:</b> <code>{get_count}</code>\n<b>На сумму:</b> <code>{amount_pay} руб.</code>\n\n<b>📃Чек:</b> <code>#{receipt}</code>')
    delete_msg = await call.message.answer("<b>🔄 Ждите, товары подготавливаются</b>")
    message_id = int(call.data.split(":")[3])

    await bot.delete_message(call.message.chat.id, message_id)
    await call.message.delete()

    if 1 <= int(get_count) <= len(get_items):
        if int(get_user[4]) >= amount_pay:
            save_items, send_count, split_len = buy_itemx(get_items, get_count)

            if split_len <= 50:
                split_len = 70
            elif split_len <= 100:
                split_len = 50
            elif split_len <= 150:
                split_len = 30
            elif split_len <= 200:
                split_len = 10
            else:
                split_len = 3
            
            if get_count != send_count:
                amount_pay = int(get_position[3]) * send_count
                get_count = send_count

            buy_time = get_dates()

            await bot.delete_message(call.from_user.id, delete_msg.message_id)

            if len(save_items) <= split_len:
                send_message = "\n".join(save_items)
                await call.message.answer(f"<b>💙 Ваши товары:</b>\n"
                                          f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                          f"{send_message}")
            else:
                await call.message.answer(f"<b>💙 Ваши товары:</b>\n"
                                          f"➖➖➖➖➖➖➖➖➖➖➖➖➖")

                save_split_items = split_messages(save_items, split_len)
                for item in save_split_items:
                    send_message = "\n".join(item)
                    await call.message.answer(send_message)
            save_items = "\n".join(save_items)

            add_purchasex(call.from_user.id, call.from_user.username, call.from_user.first_name,
                          receipt, get_count, amount_pay, get_position[3], get_position[1], get_position[2],
                          save_items, get_user[4], int(get_user[4]) - amount_pay, buy_time, int(time.time()))
            update_userx(call.from_user.id, balance=get_user[4] - amount_pay)
            await call.message.answer(f"<b>💙 Вы успешно купили товар(ы) ✅</b>\n"
                                      f"➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
                                      f"📃 Чек: <code>#{receipt}</code>\n"
                                      f"🏷 Название товара: <code>{get_position[2]}</code>\n"
                                      f"📦 Куплено товаров: <code>{get_count}</code>\n"
                                      f"💵 Сумма покупки: <code>{amount_pay}руб</code>\n"
                                      f"👤 Покупатель: <a href='tg://user?id={get_user[1]}'>{get_user[3]}</a> <code>({get_user[1]})</code>\n"
                                      f"🕜 Дата покупки: <code>{buy_time}</code>",
                                      reply_markup=check_user_out_func(call.from_user.id))
        else:
            await call.message.answer("<b>❗ На вашем счёте недостаточно средств</b>")
    else:
        await state.finish()
        await call.message.answer("<b>💙 Товар который вы хотели купить закончился или изменился.</b>",
                                  check_user_out_func(call.from_user.id))
