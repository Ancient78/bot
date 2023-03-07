import logging
import urllib.parse
from string import Template
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, \
    CallbackQueryHandler

import data
import oders
import sql
import storage
from sql import get_id_list, add_user, get_unpassed

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
my_filters = filters.User()
master_user = [1553590834, 449379851]


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        text = "Меню новичок:\n" \
               "/help - Текущее руководство\n" \
               "/start - Начало работы с ботом\n" \
               "/reg - Регистрация для продолжения общения в этом чате\n" \
               "/link - Получить ссылку на этот бот\n" \
               "\nМеню пользователя:\n" \
               "/help - Текущее руководство\n" \
               "/link - Получить ссылку на этот бот\n" \
               "/begin_orders - Начать сборку заказа\n" \
               "/end_orders - Закончить сборку заказа\n" \
               "/my_orders - Просмотреть мой заказ\n" \
               "/change_count - Изменить количество в заказе\n" \
               "/del_row_from_order - Удалить строку заказа\n" \
               "\nМастер-меню:\n" \
               "/start - Начало работы (ознакомительное)\n" \
               "/help - Текущее руководтсво\n" \
               "/reg - Регистрация\n" \
               "/pass_user - Одобрить пользователя\n" \
               "/get_all - Получить списки всех пользователей\n" \
               "/drop_table - Удалить таблицу пользователей\n" \
               "/link - Получить ссылку на этот бот\n" \
               "/get_all_storage - Получить все товары с остатками\n" \
               "/drop_storage - Удалить таблицу с товарами\n" \
               "/select_storage - Добавить количество к товару\n" \
               "/add_price - Добавить цену к товару\n" \
               "/add_storage - Добавить товар (только наименование)\n" \
               "/delete_storage - Удалить конкретный товар (Нумерация слетает))\n" \
               "/begin_orders - Начать сборку заказа\n" \
               "/end_orders - Закончить сборку заказа\n" \
               "/get_all_orders - Получить все заказы, независимо от статуса\n" \
               "/drop_orders - Удалить таблицу с заказами\n" \
               "/get_unshiped - Получить все неотгруженные\n" \
               "/set_shiped - Установить заказ отгруженным\n" \
               "/get_unpaid - Получить все неоплаченные\n" \
               "/set_paid - Установить заказ оплаченным\n" \
               "/get_connection - Получить данные для связи\n" \
               "/send_message - Отправить сообщение пользователю через бот\n"
    elif sql.is_user_here(update.effective_chat.id):
        text = "Данный бот создан для возможности заказа\n" \
               "/help - Текущее руководство\n" \
               "/link - Получить ссылку на этот бот\n" \
               "/begin_orders - Начать сборку заказа\n" \
               "/end_orders - Закончить сборку заказа\n" \
               "/my_orders - Просмотреть мой заказ\n" \
               "/change_count - Изменить количество в заказе\n" \
               "/del_row_from_order - Удалить строку заказа\n"
    else:
        text = "Напоминаю - этот бот создан для личного общения. Если вы попали сюда случайно, то просто удалите " \
               "этот чат." \
               "/help - Текущее руководство\n" \
               "/start - Начало работы с ботом\n" \
               "/reg - Регистрация для продолжения общения в этом чате\n" \
               "/link - Получить ссылку на этот бот\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def get_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        table = "User id - Name\n"
        row_data = sql.get_full_table()
        index = 1
        for id, first_name, last_name, passed in row_data:
            name = ""
            if first_name is not None:
                first_name = urllib.parse.unquote(first_name)
                name = name + first_name + " "
            if last_name is not None:
                last_name = urllib.parse.unquote(last_name)
                name += last_name
            row_template = Template('$index) $id - $name passed=$passed\n')
            row = row_template.substitute(id=id, name=name, index=index, passed=passed)
            table += row
            index += 1
        await context.bot.send_message(chat_id=update.effective_chat.id, text=table)


async def reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Пользователь уже в списке")
    else:
        add_user(user_id=update.effective_chat.id, first_name=update.effective_chat.first_name,
                 last_name=update.effective_chat.last_name)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Регистрационные данные добавлены. "
                                                                              "Ждите одобрения")
        for user in master_user:
            await context.bot.send_message(chat_id=user, text="Зарегистрирован новый пользователь.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user or sql.is_user_here(update.effective_chat.id):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="\help - список доступных Вам команд.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Это личный бот.\nЕсли вы попали сюда "
                                                                              "случайно, то просто удалите этот "
                                                                              "чат.\nДля общения необходимо "
                                                                              "зарегистрироваться.")


async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        await context.bot.send_message(chat_id=update.effective_chat.id, text=context.bot.link)


async def pass_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = get_unpassed()
        keyboard_big = []
        keyboard = []
        for user_id, first_name, last_name in data_row:
            name = get_user_name(first_name, last_name)
            but = InlineKeyboardButton(name, callback_data=user_id)
            keyboard.append(but)
        if keyboard.__len__() > 0:
            keyboard_big.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Выберите одобряемого:", reply_markup=reply_markup)


def get_user_name(first_name, last_name):
    if last_name is None:
        name = urllib.parse.unquote(first_name)
    else:
        name = urllib.parse.unquote(last_name)
    return name


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    id_user = query.data
    await query.answer()
    sql.pass_user(id_user)
    update_filter()
    last_name, first_name = sql.get_full_data(id_user)
    msg = "Пользователь " + get_user_name(first_name, last_name) + " одобрен."
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
    await context.bot.send_message(chat_id=id_user, text="Вам одобрено продолжение работы.")


async def button_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    storage_id = query.data
    temp_storage_id = int(storage_id.replace("Storage ", ""))
    temp_data = {"Op": 'Storage', "storage_id": temp_storage_id}
    context.user_data.update(temp_data)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите количество:")


async def button_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    storage_id = query.data
    temp_storage_id = int(storage_id.replace("Delete ", ""))
    storage.delete_row(temp_storage_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Номенклатура удалена.")


async def button_3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    storage_id = query.data
    temp_storage_id = int(storage_id.replace("Order ", ""))
    temp_data = {"Op": 'Order', "storage_id": temp_storage_id}
    context.user_data.update(temp_data)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите количество:")


async def button_4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.data
    temp_user_id = int(user_id.replace("Ship ", ""))
    storage_id_list = []
    storage_data = oders.get_orders(user_id=temp_user_id, shipped=False, paid=False)
    for row in storage_data:
        storage_id_list.append((row[0], row[1]))
    oders.set_ship(temp_user_id)
    if len(storage_id_list) > 0:
        data.add_ship(storage_id_list)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Заказ помечен отгруженым.")


async def button_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.data
    temp_user_id = int(user_id.replace("Paid ", ""))
    storage_id_list = []
    storage_data = oders.get_orders(user_id=temp_user_id, shipped=True, paid=False)
    for row in storage_data:
        storage_id_list.append((row[0], row[1]))
    oders.set_paid(temp_user_id)
    if len(storage_id_list) > 0:
        data.add_pay(storage_id_list)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Заказ помечен оплаченым.")


async def button_6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.data
    temp_storage_index = int(user_id.replace("ChangeOrder ", ""))
    temp_data = {"Op": 'ChangeOrder', "storage_index": temp_storage_index}
    context.user_data.update(temp_data)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите новое количество:")


async def button_7(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.data
    temp_storage_index = int(user_id.replace("DeleteRow ", ""))
    storage_index = int(temp_storage_index) - 1
    storage_id, count = oders.delete_row(update.effective_chat.id, storage_index)
    storage.add_storage(storage_id, count)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Строка заказа удалена.")


async def button_8(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.data
    temp_storage_index = int(user_id.replace("AddPrice ", ""))
    temp_data = {"Op": 'AddPrice', "storage_index": temp_storage_index}
    context.user_data.update(temp_data)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите новую цену:")


async def button_9(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.data
    temp_user_id = int(user_id.replace("Connection ", ""))
    data_row = oders.get_connection(temp_user_id)
    full_text = sql.get_user_name(temp_user_id) + "\n"
    for row in data_row:
        for tel in row:
            full_text += str(tel) + "\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=full_text)


async def button_10(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.data
    temp_user_id = int(user_id.replace("SendMessage ", ""))
    temp_data = {"Op": 'SendMessage', "user_id": temp_user_id}
    context.user_data.update(temp_data)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите сообщение:")


async def passed_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        temp_storage_id = context.user_data.get("storage_id")
        op = context.user_data.get("Op")
        temp_storage_index = context.user_data.get("storage_index")
        temp_user_id = context.user_data.get("user_id")
        price, count, message, nom, tel = 0, 0, "", "", ""
        if op == 'SendMessage':
            message = update.effective_message.text
        if op == 'Order':
            count = int(update.effective_message.text)
        if op == 'Storage':
            count = int(update.effective_message.text)
        if op == 'Add':
            nom = update.effective_message.text
        if op == 'Tel':
            tel = update.effective_message.text
        if op == 'ChangeOrder':
            count = int(update.effective_message.text)
        if op == 'AddPrice':
            price = float(update.effective_message.text)
        if temp_storage_id is not None and op == 'Storage':
            if temp_storage_id > 0 and (type(count) == int or type(count) == float):
                context.user_data.pop("storage_id")
                context.user_data.pop("Op")
                storage.add_storage(temp_storage_id, count)
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Данные о товаре обновлены')
        if op == 'Add':
            storage.add_nom(nom)
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Данные о товаре обновлены')
        if op == 'Order':
            context.user_data.pop("storage_id")
            context.user_data.pop("Op")
            if not storage.make_reserve(temp_storage_id, count):
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text='Количество заказа меньше доступного')
            else:
                oders.add_order(update.effective_chat.id, temp_storage_id, count)
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Добавлены данные в заказ')
        if op == 'Tel':
            context.user_data.pop("Op")
            oders.set_tel_in_order(update.effective_chat.id, tel)
        if count != 0 and op == 'ChangeOrder':
            context.user_data.pop("Op")
            context.user_data.pop("storage_index")
            storage_index = int(temp_storage_index) - 1
            storage_id, different = oders.set_new_count(storage_index, update.effective_chat.id, count)
            storage.add_storage(storage_id, count)
        if op == 'AddPrice' and price != 0:
            context.user_data.pop("Op")
            context.user_data.pop("storage_index")
            storage.add_price(temp_storage_index, price)
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Цена обновлена.')
        if op == 'SendMessage':
            context.user_data.pop("Op")
            context.user_data.pop("user_id")
            await context.bot.send_message(chat_id=temp_user_id, text=message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Для общения стоит зарегистрироваться.')


async def drop_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        sql.drop_tables()
        set_master()
        update_filter()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Таблица уничтожена.")


async def get_all_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        table = "Наименование - количество - Цена(руб.)\n"
        data_row = storage.get_all_storage()
        row_template = Template("$id)$Nom - $count - $price")
        for index_id, nom, count, price in data_row:
            row = row_template.substitute(id=index_id, Nom=nom, count=count, price=price)
            table = table + row + "\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=table)


async def drop_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        storage.drop_table()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Таблица товаров очищена.")


async def add_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        temp_data = {"Op": 'Add'}
        context.user_data.update(temp_data)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Введите наименование в формате - Наименование (Объем)")


async def select_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = storage.get_all_storage()
        keyboard_big = []
        for storage_id, nom, count, price in data_row:
            keyboard = []
            text_template = Template("$id)$Nom - $count - $price")
            text = text_template.substitute(id=storage_id, Nom=nom, count=count, price=price)
            but = InlineKeyboardButton(text, callback_data="Storage " + str(storage_id))
            keyboard.append(but)
            keyboard_big.append(keyboard)
        if keyboard_big.__len__() > 0:
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список товара:", reply_markup=reply_markup)


async def add_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = storage.get_all_storage()
        keyboard_big = []
        for storage_id, nom, count, price in data_row:
            keyboard = []
            text_template = Template("$id)$Nom - $count - $price")
            text = text_template.substitute(id=storage_id, Nom=nom, count=count, price=price)
            but = InlineKeyboardButton(text, callback_data="AddPrice " + str(storage_id))
            keyboard.append(but)
            keyboard_big.append(keyboard)
        if keyboard_big.__len__() > 0:
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список товара:", reply_markup=reply_markup)


async def delete_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = storage.get_all_storage()
        keyboard_big = []
        keyboard = []
        for storage_id, nom, count, price in data_row:
            text_template = Template("$id)$Nom - $count - $price")
            text = text_template.substitute(id=storage_id, Nom=nom, count=count, price=price)
            but = InlineKeyboardButton(text, callback_data="Delete " + str(storage_id))
            keyboard.append(but)
        if keyboard.__len__() > 0:
            keyboard_big.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список товара:", reply_markup=reply_markup)


async def drop_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        oders.drop_table()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Таблица заказов удалена.")


async def begin_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        data_row = storage.get_all_storage()
        keyboard_big = []
        for storage_id, nom, count, price in data_row:
            keyboard = []
            text_template = Template("$id)$Nom - $count - $price")
            text = text_template.substitute(id=storage_id, Nom=nom, count=count, price=price)
            but = InlineKeyboardButton(text, callback_data="Order " + str(storage_id))
            keyboard.append(but)
            keyboard_big.append(keyboard)
        if keyboard_big.__len__() > 0:
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список товара:", reply_markup=reply_markup)


async def end_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        temp_data = {"Op": 'Tel'}
        context.user_data.update(temp_data)
        await context.bot.send_message(update.effective_chat.id,
                                       text="Введите телефон для связи, если хотите, чтобы Вам перезвонили. В ином "
                                            "случае с Вами свяжутся через Телеграмм.")
        for user in master_user:
            await context.bot.send_message(chat_id=user, text="Зафиксирован новый заказ.")


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        data_row = oders.get_orders(user_id=update.effective_chat.id, shipped=False, paid=False)
        full_text = ""
        index = 1
        full_cost = 0
        for _, user_id, storage_id, count, cost, _, _, _ in data_row:
            temp_text = Template("$index)$nom - $count - $cost\n")
            full_text += temp_text.substitute(index=index, nom=storage.get_storage_name(storage_id).lstrip(),
                                              count=count, cost=cost)
            index += 1
            full_cost += cost
        if full_text != "":
            full_text += "Общая стоимость: "
            full_text += str(full_cost)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=full_text)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Нет заказанных товаров.")


async def change_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        data_row = oders.get_orders(user_id=update.effective_chat.id, shipped=False, paid=False)
        keyboard_big = []
        keyboard = []
        index = 1
        for _, user_id, storage_id, count, _, _, _ in data_row:
            text_template = Template("$index)$nom - $count\n")
            text = text_template.substitute(index=index, nom=storage.get_storage_name(storage_id).lstrip(), count=count)
            but = InlineKeyboardButton(text, callback_data="ChangeOrder " + str(index))
            keyboard.append(but)
            index += 1
        if keyboard.__len__() > 0:
            keyboard_big.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список товара:", reply_markup=reply_markup)


async def del_row_from_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        data_row = oders.get_orders(user_id=update.effective_chat.id, shipped=False, paid=False)
        keyboard_big = []
        keyboard = []
        index = 1
        for _, user_id, storage_id, count, _, _, _ in data_row:
            text_template = Template("$index)$nom - $count\n")
            text = text_template.substitute(index=index, nom=storage.get_storage_name(storage_id).lstrip(), count=count)
            but = InlineKeyboardButton(text, callback_data="DeleteRow " + str(index))
            keyboard.append(but)
            index += 1
        if keyboard.__len__() > 0:
            keyboard_big.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список товара:", reply_markup=reply_markup)


async def get_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = oders.get_orders()
        full_text = ""
        full_cost = 0
        user_list = {}
        for order_id, user_id, storage_id, count, cost, shipped, paid, tel in data_row:
            if user_list.get(user_id) is None:
                user_list[user_id] = [(storage_id, cost)]
            else:
                user_list[user_id] = user_list.get(user_id).__add__([(storage_id, cost)])
        for user_id in user_list.keys():
            full_text += "_____\n" + "<b>" + sql.get_user_name(user_id) + "</b>\n\n"
            local_cost = 0
            for d in user_list.get(user_id):
                full_text += "<i>" + storage.get_storage_name(d[0]) + " - " + str(d[1]) + "</i>\n"
                local_cost += d[1]
            full_text += "\n<i>Стоимость: " + str(local_cost) + "</i>\n"
            full_cost += local_cost
        full_text += "_____\nОбщая стоимость: " + str(full_cost) + "\n"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=full_text, parse_mode='HTML')


async def get_unshiped(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = oders.get_orders(shipped=False)
        full_text = ""
        full_cost = 0
        user_list = {}
        for order_id, user_id, storage_id, count, cost, shipped, paid, tel in data_row:
            if user_list.get(user_id) is None:
                user_list[user_id] = [(storage_id, cost)]
            else:
                user_list[user_id] = user_list.get(user_id).__add__([(storage_id, cost)])
        for user_id in user_list.keys():
            full_text += "_____\n" + "<b>" + sql.get_user_name(user_id) + "</b>\n\n"
            local_cost = 0
            for d in user_list.get(user_id):
                full_text += "<i>" + storage.get_storage_name(d[0]) + " - " + str(d[1]) + "</i>\n"
                local_cost += d[1]
            full_text += "\n<i>Стоимость: " + str(local_cost) + "</i>\n"
            full_cost += local_cost
        full_text += "_____\nОбщая стоимость: " + str(full_cost) + "\n"
        if full_text != "":
            await context.bot.send_message(chat_id=update.effective_chat.id, text=full_text, parse_mode='HTML')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Нет неотгруженных товаров.")


async def get_unpaid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = oders.get_orders(shipped=False)
        full_text = ""
        full_cost = 0
        user_list = {}
        for order_id, user_id, storage_id, count, cost, shipped, paid, tel in data_row:
            if user_list.get(user_id) is None:
                user_list[user_id] = [(storage_id, cost)]
            else:
                user_list[user_id] = user_list.get(user_id).__add__([(storage_id, cost)])
        for user_id in user_list.keys():
            full_text += "_____\n" + "<b>" + sql.get_user_name(user_id) + "</b>\n\n"
            local_cost = 0
            for d in user_list.get(user_id):
                full_text += "<i>" + storage.get_storage_name(d[0]) + " - " + str(d[1]) + "</i>\n"
                local_cost += d[1]
            full_text += "\n<i>Стоимость: " + str(local_cost) + "</i>\n"
            full_cost += local_cost
        full_text += "_____\nОбщая стоимость: " + str(full_cost) + "\n"
        if full_text != "":
            full_text += "Общая стоимость: "
            full_text += str(full_cost)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=full_text, parse_mode='HTML')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Нет неоплаченных товаров.")


async def set_shiped(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = oders.get_orders(shipped=False)
        orders = {}
        for _, user_id, storage_id, count, cost, _, _, _ in data_row:
            new_order = storage.get_storage_name(storage_id) + " - " + str(count)
            if orders.get(user_id) is None:
                orders[user_id] = (sql.get_user_name(user_id), new_order)
            else:
                orders[user_id] = orders.get(user_id) + (new_order,)
        keyboard_big = []
        keyboard = []
        for user_id in orders.keys():
            text_button = ""
            for i in range(orders[user_id].__len__()):
                text_button = text_button + orders.get(user_id)[i] + " "
            but = InlineKeyboardButton(text_button, callback_data="Ship " + str(user_id))
            keyboard.append(but)
        if keyboard.__len__() > 0:
            keyboard_big.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список заказов:", reply_markup=reply_markup)


async def set_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = oders.get_orders(shipped=True, paid=False)
        orders = {}
        for _, user_id, storage_id, count, cost, _, _, _ in data_row:
            new_order = storage.get_storage_name(storage_id) + " - " + str(count)
            if orders.get(user_id) is None:
                orders[user_id] = (sql.get_user_name(user_id), new_order)
            else:
                orders[user_id] = orders.get(user_id) + (new_order,)
        keyboard_big = []
        keyboard = []
        for user_id in orders.keys():
            text_button = ""
            for i in range(orders[user_id].__len__()):
                text_button = text_button + orders.get(user_id)[i] + " "
            but = InlineKeyboardButton(text_button, callback_data="Paid " + str(user_id))
            keyboard.append(but)
        if keyboard.__len__() > 0:
            keyboard_big.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список отгруженных заказов:", reply_markup=reply_markup)


async def get_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = oders.get_orders(paid=True)
        users = set()
        for _, user_id, storage_id, count, cost, _, _, _ in data_row:
            users.add(user_id)

        keyboard_big = []
        keyboard = []
        for user_id in users:
            text_button = sql.get_user_name(user_id)
            but = InlineKeyboardButton(text_button, callback_data="Connection " + str(user_id))
            keyboard.append(but)
        if keyboard.__len__() > 0:
            keyboard_big.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список пользователей, оплативших заказ:", reply_markup=reply_markup)


async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data_row = oders.get_orders()
        users = set()
        for _, user_id, storage_id, count, cost, _, _, _ in data_row:
            users.add(user_id)

        keyboard_big = []
        keyboard = []
        for user_id in users:
            text_button = sql.get_user_name(user_id)
            but = InlineKeyboardButton(text_button, callback_data="SendMessage " + str(user_id))
            keyboard.append(but)
        if keyboard.__len__() > 0:
            keyboard_big.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список пользователей:", reply_markup=reply_markup)


async def clear_shiped(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        oders.clear_shiped()


async def clear_paid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        oders.clear_paid()


async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=data.get_date())


async def drop_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data.drop_table()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Таблица дат очищена")


def add_text_handler():
    update_filter()
    passed_user_handler = MessageHandler(my_filters, passed_user)
    application.add_handler(passed_user_handler)


def update_filter():
    dlist: List = get_id_list()
    for dl in dlist:
        my_filters.add_user_ids(dl)


def set_master():
    res = sql.get_master()
    len_res = res.__len__()
    if len_res == 0:
        # 1553590834, 449379851
        sql.add_user(1553590834, "Мастер 2", None)
        sql.add_user(449379851, "Мастер 1", None)
        sql.pass_user('1553590834')
        sql.pass_user('449379851')
    elif len_res == 1:
        name = sql.get_user_name(449379851)
        if name == "":
            sql.add_user(449379851, "Мастер 1", None)
            sql.pass_user('449379851')
        name = sql.get_user_name(1553590834)
        if name == "":
            sql.add_user(1553590834, "Мастер 2", None)
            sql.pass_user('1553590834')


if __name__ == '__main__':
    application = ApplicationBuilder().token('6259243866:AAGPoyRHAP9MKOL1J7kyEQRO8r6kQV47CtE').build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler("reg", reg))
    application.add_handler(CommandHandler("pass_user", pass_user))
    application.add_handler(CommandHandler("get_all", get_all))
    application.add_handler(CommandHandler("drop_table", drop_table))
    application.add_handler(CommandHandler("link", link))
    application.add_handler(CommandHandler("get_all_storage", get_all_storage))
    application.add_handler(CommandHandler("drop_storage", drop_storage))
    application.add_handler(CommandHandler("select_storage", select_storage))
    application.add_handler(CommandHandler("add_storage", add_storage))
    application.add_handler(CommandHandler("delete_storage", delete_storage))
    application.add_handler(CommandHandler("begin_orders", begin_orders))
    application.add_handler(CommandHandler("get_all_orders", get_all_orders))
    application.add_handler(CommandHandler("get_unshiped", get_unshiped))
    application.add_handler(CommandHandler("get_unpaid", get_unpaid))
    application.add_handler(CommandHandler("drop_orders", drop_orders))
    application.add_handler(CommandHandler("end_orders", end_orders))
    application.add_handler(CommandHandler("set_shiped", set_shiped))
    application.add_handler(CommandHandler("set_paid", set_paid))
    application.add_handler(CommandHandler("my_orders", my_orders))
    application.add_handler(CommandHandler("change_count", change_count))
    application.add_handler(CommandHandler("del_row_from_order", del_row_from_order))
    application.add_handler(CommandHandler("add_price", add_price))
    application.add_handler(CommandHandler("get_connection", get_connection))
    application.add_handler(CommandHandler("send_message", send_message))
    application.add_handler(CommandHandler("clear_shiped", clear_shiped))
    application.add_handler(CommandHandler("clear_paid", clear_paid))
    application.add_handler(CommandHandler("get_date", get_date))
    application.add_handler(CommandHandler("drop_date", drop_date))
    set_master()
    add_text_handler()
    application.add_handler(CallbackQueryHandler(button_10, pattern="SendMessage \d+"))
    application.add_handler(CallbackQueryHandler(button_9, pattern="Connection \d+"))
    application.add_handler(CallbackQueryHandler(button_8, pattern="AddPrice \d+"))
    application.add_handler(CallbackQueryHandler(button_7, pattern="DeleteRow \d+"))
    application.add_handler(CallbackQueryHandler(button_6, pattern="ChangeOrder \d+"))
    application.add_handler(CallbackQueryHandler(button_5, pattern="Paid \d+"))
    application.add_handler(CallbackQueryHandler(button_4, pattern="Ship \d+"))
    application.add_handler(CallbackQueryHandler(button_3, pattern="Order \d+"))
    application.add_handler(CallbackQueryHandler(button_2, pattern="Delete \d+"))
    application.add_handler(CallbackQueryHandler(button_1, pattern="Storage \d+"))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()
