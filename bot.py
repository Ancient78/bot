import logging
import signal
import urllib.parse
from string import Template
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters, MessageHandler, \
    CallbackQueryHandler

import oders
import sql
import storage
from sql import get_id_list, add_user, get_unpassed

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
my_filters = filters.User()
master_user = [1553590834, 449379851]


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        text = "/start - Начало работы (ознакомительное)\n" \
               "/help - Текущее руководтсво\n" \
               "/reg - Регистрация\n" \
               "/pass_user - Одобрить пользователя\n" \
               "/get_all - Получить списки всех пользователей\n" \
               "/drop_table - Удалить таблицу пользователей\n" \
               "/link - Получить ссылку на этот бот\n" \
               "/get_all_storage - Получить все товары с остатками\n" \
               "/drop_storage - Удалить таблицу с товарами\n" \
               "/select_storage - Добавить количество к товару\n" \
               "/add_storage - Добавить товар (только наименование)\n" \
               "/delete_storage - Удалить конкретный товар (Нумерация слетает))\n" \
               "/begin_orders - Начать сборку заказа\n" \
               "/end_orders - Закончить сборку заказа\n" \
               "/get_all_orders - Получить все заказы, независимо от статуса\n" \
               "/drop_orders - Удалить таблицу с заказами\n" \
               "/get_unshiped - Получить все неотгруженные\n" \
               "/set_shiped - Установить заказ отгруженным\n" \
               "/get_unpaid - Получить все неоплаченные\n" \
               "/set_paid - Установить заказ оплаченным\n"
    elif sql.is_user_here(update.effective_chat.id):
        text = "Данный бот создан для возможности заказа\n" \
               "/help - Текущее руководство\n" \
               "/link - Получить ссылку на этот бот\n" \
               "/begin_orders - Начать сборку заказа\n" \
               "/end_orders - Закончить сборку заказа\n" \
               "/my_orders - Просмотреть мой заказ" \
               "/change_count - изменить количество в заказе" \
               "/del_row_orders - удалить строку заказа"
    else:
        text="Напоминаю - этот бот создан для личного общения. Если вы попали сюда случайно, то просто удалите этот чат." \
             "/help - Текущее руководство\n" \
             "/start - Начало работы с ботом\n" \
             "/reg - Регистрация для продолжения общения в этом чате\n" \
             "/link - Получить ссылку на этот бот\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)


async def get_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        table = "User id - Name\n"
        data = sql.get_full_table()
        index = 1
        for id, first_name, last_name, passed in data:
            name = ""
            if first_name is not None:
                first_name = urllib.parse.unquote(first_name)
                name = name + first_name + " "
            if last_name is not None:
                last_name = urllib.parse.unquote(last_name)
                name += last_name
            row_template = Template('$index) $id - $name\n')
            row = row_template.substitute(id=id, name=name, index=index)
            table += row
            index+=1
        await context.bot.send_message(chat_id=update.effective_chat.id, text=table)


async def reg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Пользователь уже в списке")
    else:
        add_user(user_id=update.effective_chat.id, first_name=update.effective_chat.first_name,
             last_name=update.effective_chat.last_name)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Регистрационные данные добавлены. Ждите одобрения")
        await context.bot.send_message(chat_id=master_user, text="Зарегистрирован новый пользователь.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user or sql.is_user_here(update.effective_chat.id):
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="\help - список доступных Вам команд.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Это личный бот.\nЕсли вы попали сюда случайно, то просто удалите этот чат.\nДля общения необходимо зарегистрироваться.")


async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        await context.bot.send_message(chat_id=update.effective_chat.id, text = context.bot.link)


async def pass_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data = get_unpassed()
        keyboard_big = []
        keyboard = []
        for id, first_name, last_name in data:
            name = get_user_name(first_name, last_name)
            but = InlineKeyboardButton(name, callback_data=id)
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
    query = update.callback_query
    user_id = query.data
    temp_user_id = int(user_id.replace("Ship ", ""))
    oders.set_ship(temp_user_id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Заказ помечен отгруженым.")


async def button_5(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        user_id = query.data
        temp_user_id = int(user_id.replace("Paid ", ""))
        oders.set_paid(temp_user_id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Заказ помечен оплаченым.")


async def passed_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        temp_storage_id = context.user_data.get("storage_id")
        op = context.user_data.get("Op")
        if op == 'Order': count = int(update.effective_message.text)
        if op == 'Storage': count = int(update.effective_message.text)
        if op == 'Add': nom = update.effective_message.text
        if op == 'Tel': tel = update.effective_message.text
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
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Количество заказа меньше доступного')
            else:
                oders.add_order(update.effective_chat.id, temp_storage_id, count)
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Добавлены данные в заказ')
        if op == 'Tel':
            context.user_data.pop("Op")
            oders.set_tel_in_order(update.effective_chat.id, tel)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Для общения стоит зарегистрироваться.')


async def drop_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        sql.drop_tables()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Таблица уничтожена.")


async def get_all_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        table = "Наименование - количество\n"
        data = storage.get_all_storage()
        row_template = Template("$id)$Nom - $count")
        for id, nom, count in data:
            row = row_template.substitute(id=id, Nom=nom, count=count)
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Введите наименование в формате - Наименование (Объем)")


async def select_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data = storage.get_all_storage()
        keyboard_big = []
        keyboard = []
        for storage_id, nom, count in data:
            text_template = Template("$id)$Nom - $count")
            text = text_template.substitute(id=storage_id, Nom=nom, count=count)
            but = InlineKeyboardButton(text, callback_data="Storage " + str(storage_id))
            keyboard.append(but)
        if keyboard.__len__() > 0:
            keyboard_big.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список товара:", reply_markup=reply_markup)


async def delete_storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data = storage.get_all_storage()
        keyboard_big = []
        keyboard = []
        for storage_id, nom, count in data:
            text_template = Template("$id)$Nom - $count")
            text = text_template.substitute(id=storage_id, Nom=nom, count=count)
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
        data = storage.get_all_storage()
        keyboard_big = []
        keyboard = []
        for storage_id, nom, count in data:
            text_template = Template("$id)$Nom - $count")
            text = text_template.substitute(id=storage_id, Nom=nom, count=count)
            but = InlineKeyboardButton(text, callback_data="Order " + str(storage_id))
            keyboard.append(but)
        if keyboard.__len__() > 0:
            keyboard_big.append(keyboard)
            reply_markup = InlineKeyboardMarkup(keyboard_big)
            await update.message.reply_text("Список товара:", reply_markup=reply_markup)


async def end_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        temp_data = {"Op": 'Tel'}
        context.user_data.update(temp_data)
        await context.bot.send_message(update.effective_chat.id, text="Введите телефон для связи, если хотите, чтобы Вам перезвонили. В ином случае с Вами свяжутся через Телеграмм.")


async def my_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if sql.is_user_here(update.effective_chat.id):
        data = oders.get_orders(user_id=update.effective_chat.id, shipped=False, paid=False)
        full_text = ""
        index = 1
        for _, user_id, storage_id, count, _, _, _ in data:
            temp_text = Template("$index)$nom - $count\n")
            full_text += temp_text.substitute(index=index, nom=storage.get_storage_name(storage_id).lstrip(), count=count)
            index+=1
        if full_text != "":
            await context.bot.send_message(chat_id=update.effective_chat.id, text=full_text)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Нет заказанных товаров.")


async def get_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data = oders.get_orders()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=data)


async def get_unshiped(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data = oders.get_orders(shipped=False)
        #Пользователь - Номенклатура - Количество
        full_text = ""
        for _, user_id, storage_id, count, _, _, _ in data:
            temp_text = Template("$user - $nom - $count\n")
            full_text += temp_text.substitute(user=sql.get_user_name(user_id), nom=storage.get_storage_name(storage_id), count=count)
        if full_text!="":
            await context.bot.send_message(chat_id=update.effective_chat.id, text=full_text)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Нет неотгруженных товаров.")


async def get_unpaid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data = oders.get_orders(paid=False)
        full_text = ""
        for _, user_id, storage_id, count, _, _, _ in data:
            temp_text = Template("$user - $nom - $count\n")
            full_text += temp_text.substitute(user=sql.get_user_name(user_id), nom=storage.get_storage_name(storage_id), count=count)
        if full_text!="":
            await context.bot.send_message(chat_id=update.effective_chat.id, text=full_text)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Нет неоплаченных товаров.")


async def set_shiped(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in master_user:
        data = oders.get_orders(shipped=True)
        orders = {}
        for _, user_id, storage_id, count, _, _, _ in data:
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
        data = oders.get_orders(shipped=True, paid=False)
        orders = {}
        for _, user_id, storage_id, count, _, _, _ in data:
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


def add_text_handler():
    update_filter()
    passed_user_handler = MessageHandler(my_filters, passed_user)
    application.add_handler(passed_user_handler)


def update_filter():
    dlist: List = get_id_list()
    for dl in dlist:
        my_filters.add_user_ids(dl)


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
    add_text_handler()
    application.add_handler(CallbackQueryHandler(button_5, pattern="Paid \d+"))
    application.add_handler(CallbackQueryHandler(button_4, pattern="Ship \d+"))
    application.add_handler(CallbackQueryHandler(button_3, pattern="Order \d+"))
    application.add_handler(CallbackQueryHandler(button_2, pattern="Delete \d+"))
    application.add_handler(CallbackQueryHandler(button_1, pattern="Storage \d+"))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()
