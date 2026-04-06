data = open('/Users/vusso/freshbar_bot/freshbar_bot.py').read()
old = """💳 Перевод по СБП:\nБанк: Сбербанк\nТелефон: +7(XXX)XXX-XX-XX\n\n💳 На карту:\nXXXX XXXX XXXX XXXX\n\nПосле перевода отправьте скриншот сюда."""
new = """🇷🇺 СБП (Россия):\nБанк: Сбербанк\nТел: +7 922 402 3939\nПолучатель: Юлия А.\n\n🌍 KoronaPay (СНГ):\nПриложение Korona\nКарта: 4279 3806 2999 2522\nПолучатель: Alieva Julia\n\n💲 USDT (TRC-20):\nTE2p58Upz2AEAwd2EtpShERmr946vxskcp\n\nПосле перевода отправьте скриншот сюда."""
data = data.replace(old, new)
f = open('/Users/vusso/freshbar_bot/freshbar_bot.py', 'w')
f.write(data)
f.close()
print("✅ Реквизиты обновлены!")
