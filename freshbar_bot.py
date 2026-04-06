import os, json, logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters

BOT_TOKEN = "8784970404:AAGejLNFWN3WYRyx5Hh0plUQrUheMZiWcPM"
ADMIN_CHAT_ID = 372533853
ADMIN_IDS = [372533853, 1022880219]
NOTIFY_USERNAMES = ["Vusso", "juliareir"]
PRICES_PER_UNIT = 990
DISCOUNT = {1:990, 2:1890, 3:2790, 4:3490, 5:4190, 6:4890}
PAYMENT_DETAILS = "\n".join(["","\U0001f1f7\U0001f1fa СБП (Россия):","Банк: Сбербанк","Тел: +7 922 402 3939","Получатель: Юлия А.","","\U0001f30d KoronaPay (СНГ):","Приложение Korona","Карта: 4279 3806 2999 2522","Получатель: Alieva Julia","","\U0001f4b2 USDT (TRC-20):","TE2p58Upz2AEAwd2EtpShERmr946vxskcp","","После перевода отправьте скриншот сюда."])
logging.basicConfig(format="%(asctime)s-%(name)s-%(levelname)s-%(message)s", level=logging.INFO)
CHOOSE_FLAVOR,CHOOSE_MORE,CHOOSE_QTY_SINGLE,ENTER_NAME,ENTER_PHONE,ENTER_ADDRESS,CONFIRM_ORDER,AWAITING_PAYMENT=range(8)
orders={}
order_counter=0
FLAVORS={
    "mint":{"name":"Arctic Mint","emoji":"\U0001f9ca","desc":"Мощный ледяной удар мяты и ментола — заменяет ощущение сигареты","badge":"\U0001f525 Хит"},
    "lime":{"name":"Basil Lime","emoji":"\U0001f34b","desc":"Свежий цитрусовый микс с базиликом и травяными нотами","badge":"\U0001f195"},
    "grape":{"name":"Grape Ice","emoji":"\U0001f347","desc":"Сладкий сочный виноград с лёгкой прохладой","badge":""},
    "peach":{"name":"Peach Blossom","emoji":"\U0001f351","desc":"Нежный персиковый аромат с цветочными нотами","badge":""}
}

def get_price(qty):
    if qty in DISCOUNT: return DISCOUNT[qty]
    return qty * 690

def cart_text(cart):
    lines=[]
    for item in cart:
        f=FLAVORS[item]
        lines.append(f"{f['emoji']} {f['name']}")
    return ", ".join(lines)

WELCOME="""\U0001f33f InQ — ароматический ингалятор

Тысячи людей уже бросили курить, заменив сигареты на мятные ароматические ингаляторы. Теперь ваша очередь.

\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501

\U0001f9ea Как это работает?

Внутри InQ \u2014 концентрированная формула мяты, ментола, эвкалипта и эфирных масел. При вдохе вы получаете тот самый ледяной \u00abзатяг\u00bb и свежесть в лёгких \u2014 точно как от ментоловой сигареты.

Ваш мозг обманывается: получает привычный сигнал прохлады и расслабления, думает что получил сигарету. Но внутри \u2014 ноль никотина, ноль дыма, ноль вреда.

Ритуал остаётся, ощущения остаются \u2014 а зависимость уходит.

\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501

\u2705 Состав: эфирные масла мяты + ментол + эвкалипт
\u2705 Никотина: 0%. Табака: 0%. Дыма: 0%
\u2705 Хватает на 2-3 месяца
\u2705 Карманный формат \u2014 размер AirPods-кейса
\u2705 4 уникальных вкуса
\u2705 Доставка по всей РФ и СНГ за 7-14 дней

\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501

\U0001f525 Сегодня скидка 47%: 990р вместо 1890р
\U0001f6d2 Нажмите кнопку ниже, чтобы заказать:"""

async def start(update,context):
    kb=[[InlineKeyboardButton("\U0001f6d2 ЗАКАЗАТЬ СО СКИДКОЙ -47%",callback_data="order_start")],[InlineKeyboardButton("\U0001f33f Каталог вкусов",callback_data="catalog")],[InlineKeyboardButton("\u2753 FAQ",callback_data="faq"),InlineKeyboardButton("\U0001f4ac Написать нам",url="https://t.me/Vusso")],[InlineKeyboardButton("\U0001f310 Наш сайт",url="https://freshbar-store.netlify.app")]]
    await update.message.reply_text(WELCOME,reply_markup=InlineKeyboardMarkup(kb))
    return ConversationHandler.END

async def show_catalog(update,context):
    q=update.callback_query;await q.answer()
    t="\U0001f33f КАТАЛОГ InQ\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
    for v in FLAVORS.values():
        b=f" {v['badge']}" if v['badge'] else ""
        t+=f"{v['emoji']} {v['name']}{b}\n{v['desc']}\n\n"
    t+="\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\U0001f4b0 Цены:\n\n\u2022 1 шт \u2014 990р (скидка 47%!)\n\u2022 2 шт \u2014 1 890р\n\u2022 3 шт \u2014 2 790р\n\u2022 4 шт \u2014 3 490р (все 4 вкуса!)\n\n\U0001f69a Бесплатная доставка от 2 шт!\n\u23f3 Одного InQ хватает на 2-3 месяца"
    await q.edit_message_text(t,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\U0001f6d2 ЗАКАЗАТЬ",callback_data="order_start")],[InlineKeyboardButton("\u25c0\ufe0f Назад",callback_data="back_to_menu")]]))

async def show_faq(update,context):
    q=update.callback_query;await q.answer()
    t="\u2753 ЧАСТЫЕ ВОПРОСЫ\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
    t+="\U0001f4a1 Это реально помогает бросить курить?\nInQ \u2014 это не лекарство, а ароматический ингалятор. Но принцип работает: формула мяты и ментола создаёт в лёгких ощущение, идентичное затяжке ментоловой сигареты. Мозг получает привычный сигнал и перестаёт требовать сигарету. Тысячи людей уже заменили привычку таким способом.\n\n"
    t+="\U0001f9ea Что внутри?\nНатуральные эфирные масла мяты, ментол, эвкалипт. Никотина 0%, табака 0%, химии 0%.\n\n"
    t+="\u23f0 На сколько хватает?\n2-3 месяца при 10-20 использованиях в день.\n\n"
    t+="\U0001f69a Как быстро доставят?\nРФ: 7-14 дней | СНГ: 10-18 дней. Трек-номер после оплаты.\n\n"
    t+="\U0001f504 Если не подойдёт?\nВозврат 14 дней, без вопросов.\n\n"
    t+="\U0001f6ab Безопасно?\nДа. Никакого дыма, пара или химии. Только аромат эфирных масел."
    await q.edit_message_text(t,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\U0001f6d2 ЗАКАЗАТЬ",callback_data="order_start")],[InlineKeyboardButton("\u25c0\ufe0f Назад",callback_data="back_to_menu")]]))

async def show_contact(update,context):
    q=update.callback_query;await q.answer()
    t="\U0001f4ac КОНТАКТЫ\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\nTelegram: @Vusso\nTelegram: @juliareir\n\nОтвечаем в течение 1-2 часов!"
    await q.edit_message_text(t,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\U0001f6d2 ЗАКАЗАТЬ",callback_data="order_start")],[InlineKeyboardButton("\u25c0\ufe0f Назад",callback_data="back_to_menu")]]))

async def back_to_menu(update,context):
    q=update.callback_query;await q.answer()
    kb=[[InlineKeyboardButton("\U0001f6d2 ЗАКАЗАТЬ СО СКИДКОЙ -47%",callback_data="order_start")],[InlineKeyboardButton("\U0001f33f Каталог вкусов",callback_data="catalog")],[InlineKeyboardButton("\u2753 FAQ",callback_data="faq"),InlineKeyboardButton("\U0001f4ac Контакты",callback_data="contact")],[InlineKeyboardButton("\U0001f310 Наш сайт",url="https://freshbar-store.netlify.app")]]
    await q.edit_message_text("\U0001f33f InQ \u2014 ароматический ингалятор\n\n\U0001f525 Скидка 47%: 990р вместо 1890р\n\nЗамени привычку \u2014 бросай курить легко",reply_markup=InlineKeyboardMarkup(kb))

async def order_start(update,context):
    q=update.callback_query;await q.answer()
    context.user_data["order"]={"cart":[]}
    kb=[]
    for k,v in FLAVORS.items():
        b=f" {v['badge']}" if v['badge'] else ""
        kb.append([InlineKeyboardButton(f"{v['emoji']} {v['name']}{b}",callback_data=f"add_{k}")])
    kb.append([InlineKeyboardButton("\u274c Отмена",callback_data="cancel_order")])
    await q.edit_message_text("\U0001f6d2 ОФОРМЛЕНИЕ ЗАКАЗА\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\nВыберите аромат:\n\nМожно выбрать несколько \u2014 добавляйте по одному",reply_markup=InlineKeyboardMarkup(kb))
    return CHOOSE_FLAVOR

async def add_flavor(update,context):
    q=update.callback_query;await q.answer()
    c=q.data.replace("add_","")
    context.user_data["order"]["cart"].append(c)
    cart=context.user_data["order"]["cart"];qty=len(cart);price=get_price(qty);ct=cart_text(cart)
    kb=[]
    for k,v in FLAVORS.items():
        b=f" {v['badge']}" if v['badge'] else ""
        kb.append([InlineKeyboardButton(f"+ {v['emoji']} {v['name']}{b}",callback_data=f"add_{k}")])
    kb.append([InlineKeyboardButton(f"\u2705 Готово \u2014 оформить {qty} шт за {price}р",callback_data="done_cart")])
    kb.append([InlineKeyboardButton("\u274c Отмена",callback_data="cancel_order")])
    await q.edit_message_text(f"\U0001f6d2 Ваша корзина ({qty} шт):\n{ct}\n\n\U0001f4b0 Сумма: {price}р\n\nДобавьте ещё аромат или нажмите Готово:",reply_markup=InlineKeyboardMarkup(kb))
    return CHOOSE_FLAVOR

async def done_cart(update,context):
    q=update.callback_query;await q.answer()
    cart=context.user_data["order"]["cart"]
    if not cart:await q.edit_message_text("Корзина пуста. /start");return ConversationHandler.END
    context.user_data["order"]["qty"]=len(cart);qty=len(cart);price=get_price(qty);ct=cart_text(cart)
    await q.edit_message_text(f"\u2705 Корзина: {ct}\n\U0001f4b0 {price}р за {qty} шт\n\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\nВаше имя?\n\nНапишите в чат:")
    return ENTER_NAME

async def enter_name(update,context):
    context.user_data["order"]["name"]=update.message.text.strip()
    await update.message.reply_text(f"\u2705 {update.message.text.strip()}, приятно познакомиться!\n\nНомер телефона с кодом вашей страны?\n\nНапример: +79221234567 или +994501234567")
    return ENTER_PHONE

async def enter_phone(update,context):
    context.user_data["order"]["phone"]=update.message.text.strip()
    await update.message.reply_text("\u2705 Записал!\n\nГород и полный адрес доставки?\n\nНапример: 101000, Москва, ул. Ленина 15, кв 42")
    return ENTER_ADDRESS

async def enter_address(update,context):
    context.user_data["order"]["address"]=update.message.text.strip()
    o=context.user_data["order"];cart=o["cart"];qty=len(cart);price=get_price(qty);ct=cart_text(cart)
    t=f"\U0001f4cb ВАШ ЗАКАЗ\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
    t+=f"\U0001f33f Товар: {ct}\n\U0001f4e6 Кол-во: {qty} шт\n\U0001f4b0 Сумма: {price}р\n\n"
    t+=f"\U0001f464 Имя: {o['name']}\n\U0001f4f1 Тел: {o['phone']}\n\U0001f4cd Адрес: {o['address']}\n\n"
    t+=f"\U0001f69a Доставка: бесплатно\n\U0001f4c5 Срок: 7-14 дней\n\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\nВсё верно?"
    await update.message.reply_text(t,reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\u2705 Подтвердить и оплатить",callback_data="confirm_order")],[InlineKeyboardButton("\u274c Отменить",callback_data="cancel_order")]]))
    return CONFIRM_ORDER

async def notify_admins(context,text,reply_markup=None):
    for uid in ADMIN_IDS:
        try:await context.bot.send_message(chat_id=uid,text=text,reply_markup=reply_markup)
        except:pass

async def confirm_order(update,context):
    global order_counter;q=update.callback_query;await q.answer();order_counter+=1
    o=context.user_data["order"];cart=o["cart"];qty=len(cart);price=get_price(qty);ct=cart_text(cart)
    o["id"]=order_counter;o["date"]=datetime.now().strftime("%d.%m.%Y %H:%M");o["user_id"]=update.effective_user.id;o["price"]=price;o["qty"]=qty;orders[order_counter]=o.copy()
    t=f"\u2705 ЗАКАЗ #{order_counter} СОЗДАН!\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
    t+=f"\U0001f4b0 К оплате: {price}р\n"
    t+=f"\n\U0001f447 Выберите удобный способ:\n{PAYMENT_DETAILS}\n\n"
    t+=f"\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
    t+=f"\U0001f4dd В комментарии: INQ-{order_counter}\n"
    t+=f"\u23f0 Оплатите в течение 60 минут\n\n"
    t+=f"\U0001f4f8 Отправьте скриншот чека сюда \U0001f447"
    await q.edit_message_text(t)
    admin_t=f"\U0001f514 НОВЫЙ ЗАКАЗ!\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"
    admin_t+=f"\U0001f4e6 #{order_counter} | {o['date']}\n{ct} ({qty} шт)\n\U0001f4b0 {price}р\n\n"
    admin_t+=f"\U0001f464 {o['name']}\n\U0001f4f1 {o['phone']}\n\U0001f4cd {o['address']}\n\U0001f4ac @{update.effective_user.username or 'нет'}"
    await notify_admins(context,admin_t)
    return AWAITING_PAYMENT

async def receive_payment(update,context):
    o=context.user_data.get("order",{});oid=o.get("id","?")
    kb=[[InlineKeyboardButton("\u2705 Подтвердить",callback_data=f"adm_ok_{oid}"),InlineKeyboardButton("\u274c Отклонить",callback_data=f"adm_no_{oid}")]]
    for uid in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=uid,text=f"\U0001f4b3 СКРИН \u2014 #{oid} от {update.effective_user.first_name} (@{update.effective_user.username or 'нет'})")
            if update.message.photo:await context.bot.send_photo(chat_id=uid,photo=update.message.photo[-1].file_id)
            elif update.message.document:await context.bot.send_document(chat_id=uid,document=update.message.document.file_id)
            await context.bot.send_message(chat_id=uid,text="Подтвердить?",reply_markup=InlineKeyboardMarkup(kb))
        except:pass
    await update.message.reply_text("\u2705 Скриншот получен!\n\nПроверим оплату за 1-2 часа.\n\n\U0001f49a Спасибо, что выбрали InQ!",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("\U0001f6d2 Заказать ещё",callback_data="order_start")]]))
    return ConversationHandler.END

async def adm_ok(update,context):
    q=update.callback_query;await q.answer()
    if update.effective_user.id not in ADMIN_IDS:return
    oid=int(q.data.replace("adm_ok_",""))
    if oid in orders:
        try:await context.bot.send_message(chat_id=orders[oid]["user_id"],text=f"\U0001f389 ЗАКАЗ #{oid} ОПЛАЧЕН!\n\nОбрабатываем заказ.\n\U0001f4e6 Трек пришлём после отправки.\n\n\U0001f49a Спасибо!")
        except:pass
    await q.edit_message_text(f"\u2705 #{oid} подтверждён")

async def adm_no(update,context):
    q=update.callback_query;await q.answer()
    if update.effective_user.id not in ADMIN_IDS:return
    oid=int(q.data.replace("adm_no_",""))
    if oid in orders:
        try:await context.bot.send_message(chat_id=orders[oid]["user_id"],text=f"\u26a0\ufe0f Заказ #{oid}\n\nОплата не подтверждена. Проверьте и отправьте скрин повторно.")
        except:pass
    await q.edit_message_text(f"\u274c #{oid} отклонён")

async def admin_orders(update,context):
    if update.effective_user.id not in ADMIN_IDS:return
    if not orders:await update.message.reply_text("\U0001f4ed Нет заказов");return
    t="\U0001f4cb ЗАКАЗЫ:\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
    for oid,o in sorted(orders.items(),reverse=True)[:10]:t+=f"\n#{oid} | {o.get('date','')} | {o.get('name','?')} | {o.get('price','?')}р"
    await update.message.reply_text(t)

async def admin_ship(update,context):
    if update.effective_user.id not in ADMIN_IDS:return
    a=context.args
    if len(a)<2:await update.message.reply_text("/ship <номер> <трек>");return
    oid,track=int(a[0]),a[1]
    if oid in orders:
        try:await context.bot.send_message(chat_id=orders[oid]["user_id"],text=f"\U0001f69a ЗАКАЗ #{oid} ОТПРАВЛЕН!\n\n\U0001f4e6 Трек: {track}\n\nОтслеживайте на сайте почты.\n\n\U0001f49a Спасибо!")
        except:pass
        await update.message.reply_text(f"\u2705 #{oid} отправлен")

async def cancel_order(update,context):
    q=update.callback_query;await q.answer();context.user_data.pop("order",None)
    await q.edit_message_text("\u274c Заказ отменён.\n\n/start чтобы начать заново")
    return ConversationHandler.END

def main():
    app=Application.builder().token(BOT_TOKEN).build()
    conv=ConversationHandler(entry_points=[CallbackQueryHandler(order_start,pattern="^order_start$")],states={CHOOSE_FLAVOR:[CallbackQueryHandler(add_flavor,pattern="^add_"),CallbackQueryHandler(done_cart,pattern="^done_cart$"),CallbackQueryHandler(cancel_order,pattern="^cancel_order$")],ENTER_NAME:[MessageHandler(filters.TEXT&~filters.COMMAND,enter_name)],ENTER_PHONE:[MessageHandler(filters.TEXT&~filters.COMMAND,enter_phone)],ENTER_ADDRESS:[MessageHandler(filters.TEXT&~filters.COMMAND,enter_address)],CONFIRM_ORDER:[CallbackQueryHandler(confirm_order,pattern="^confirm_order$"),CallbackQueryHandler(cancel_order,pattern="^cancel_order$")],AWAITING_PAYMENT:[MessageHandler(filters.PHOTO|filters.Document.ALL,receive_payment),MessageHandler(filters.TEXT&~filters.COMMAND,receive_payment)]},fallbacks=[CommandHandler("start",start),CallbackQueryHandler(cancel_order,pattern="^cancel_order$")])
    app.add_handler(conv);app.add_handler(CommandHandler("start",start));app.add_handler(CommandHandler("orders",admin_orders));app.add_handler(CommandHandler("ship",admin_ship))
    app.add_handler(CallbackQueryHandler(show_catalog,pattern="^catalog$"));app.add_handler(CallbackQueryHandler(show_faq,pattern="^faq$"));app.add_handler(CallbackQueryHandler(show_contact,pattern="^contact$"));app.add_handler(CallbackQueryHandler(back_to_menu,pattern="^back_to_menu$"))
    app.add_handler(CallbackQueryHandler(adm_ok,pattern="^adm_ok_"));app.add_handler(CallbackQueryHandler(adm_no,pattern="^adm_no_"))
    print("\U0001f680 InQ Bot запущен!");app.run_polling()

if __name__=="__main__":main()
