import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import random
from datetime import datetime
import os
import tempfile

BOT_TOKEN = "7364194056:AAFnr3nKbP2ZK2vtprumK152j4DnV3rEnBk"
bot = telebot.TeleBot(BOT_TOKEN)

DEVELOPER_LINK = "https://t.me/priknm"
QURAN_API = "https://api.alquran.cloud/v1"
ALADHAN_API = "https://api.aladhan.com/v1"
AZKAR_API = "https://raw.githubusercontent.com/nawafalqari/azkar-api/main/azkar.json"

azkar_data = None
user_ayah_audio = {}

def load_azkar():
    global azkar_data
    try:
        response = requests.get(AZKAR_API, timeout=10)
        if response.status_code == 200:
            azkar_data = response.json()
    except:
        azkar_data = None

load_azkar()

def main_menu_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📖 القرآن الكريم", callback_data="quran_menu"),
        InlineKeyboardButton("🕌 مواقيت الصلاة", callback_data="prayer_menu"),
        InlineKeyboardButton("📿 الأذكار", callback_data="azkar_menu"),
        InlineKeyboardButton("🤲 أدعية رمضان", callback_data="ramadan_duas"),
        InlineKeyboardButton("📅 التقويم الهجري", callback_data="hijri_date"),
        InlineKeyboardButton("🎲 آية عشوائية", callback_data="random_ayah"),
        InlineKeyboardButton("📻 إذاعة القرآن", callback_data="quran_radio"),
        InlineKeyboardButton("🔢 سبحة إلكترونية", callback_data="tasbeeh"),
        InlineKeyboardButton("👨‍💻 المطور", url=DEVELOPER_LINK)
    )
    return markup

def back_button(callback_data="main_menu"):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔙 رجوع", callback_data=callback_data))
    return markup

def quran_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎲 آية عشوائية", callback_data="random_ayah"),
        InlineKeyboardButton("📑 سورة بالرقم", callback_data="surah_by_number"),
        InlineKeyboardButton("🔍 بحث في القرآن", callback_data="search_quran"),
        InlineKeyboardButton("📋 قائمة السور", callback_data="surah_list"),
        InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
    )
    return markup

def azkar_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌅 أذكار الصباح", callback_data="azkar_morning"),
        InlineKeyboardButton("🌆 أذكار المساء", callback_data="azkar_evening"),
        InlineKeyboardButton("😴 أذكار النوم", callback_data="azkar_sleep"),
        InlineKeyboardButton("🕌 أذكار الصلاة", callback_data="azkar_prayer"),
        InlineKeyboardButton("🍽 أذكار الطعام", callback_data="azkar_food"),
        InlineKeyboardButton("🚶 أذكار متنوعة", callback_data="azkar_general"),
        InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
    )
    return markup

def prayer_keyboard():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📍 أدخل مدينتك", callback_data="enter_city"),
        InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
    )
    return markup

def ramadan_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌙 دعاء الإفطار", callback_data="dua_iftar"),
        InlineKeyboardButton("🍽 دعاء السحور", callback_data="dua_suhoor"),
        InlineKeyboardButton("📿 دعاء ليلة القدر", callback_data="dua_laylat_qadr"),
        InlineKeyboardButton("🤲 أدعية الصيام", callback_data="dua_fasting"),
        InlineKeyboardButton("📖 ختمة رمضان", callback_data="ramadan_khatma"),
        InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
    )
    return markup

def surah_list_keyboard(page=0):
    markup = InlineKeyboardMarkup(row_width=3)
    surahs_per_page = 15
    start = page * surahs_per_page
    end = start + surahs_per_page
    
    try:
        response = requests.get(f"{QURAN_API}/surah", timeout=10)
        if response.status_code == 200:
            surahs = response.json()['data'][start:end]
            buttons = []
            for surah in surahs:
                buttons.append(
                    InlineKeyboardButton(
                        f"{surah['number']}. {surah['name']}", 
                        callback_data=f"surah_{surah['number']}"
                    )
                )
            markup.add(*buttons)
            
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"surah_page_{page-1}"))
            if end < 114:
                nav_buttons.append(InlineKeyboardButton("➡️ التالي", callback_data=f"surah_page_{page+1}"))
            if nav_buttons:
                markup.add(*nav_buttons)
    except:
        pass
    
    markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="quran_menu"))
    return markup

def tasbeeh_keyboard(count=0):
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("📿 سبح", callback_data=f"tasbeeh_add_{count}"),
        InlineKeyboardButton(f"العدد: {count}", callback_data="tasbeeh_count"),
        InlineKeyboardButton("🔄 إعادة", callback_data="tasbeeh_reset"),
        InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
    )
    return markup

def get_random_ayah():
    try:
        ayah_num = random.randint(1, 6236)
        response = requests.get(f"{QURAN_API}/ayah/{ayah_num}/ar.alafasy", timeout=10)
        if response.status_code == 200:
            data = response.json()['data']
            return {
                'text': data['text'],
                'surah': data['surah']['name'],
                'surah_ar': data['surah']['name'],
                'ayah_num': data['numberInSurah'],
                'audio': data.get('audio', '')
            }
    except:
        pass
    return None

def get_surah(surah_number):
    try:
        response = requests.get(f"{QURAN_API}/surah/{surah_number}/ar.alafasy", timeout=15)
        if response.status_code == 200:
            return response.json()['data']
    except:
        pass
    return None

def get_prayer_times(city, country=""):
    try:
        today = datetime.now().strftime("%d-%m-%Y")
        url = f"{ALADHAN_API}/timingsByCity/{today}?city={city}&country={country}&method=4"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()['data']
            return {
                'timings': data['timings'],
                'date': data['date']['hijri'],
                'gregorian': data['date']['gregorian']
            }
    except:
        pass
    return None

def get_hijri_date():
    try:
        today = datetime.now().strftime("%d-%m-%Y")
        url = f"{ALADHAN_API}/gpiDate/{today}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()['data']['hijri']
    except:
        pass
    
    try:
        today = datetime.now().strftime("%d-%m-%Y")
        url = f"{ALADHAN_API}/timingsByCity/{today}?city=Mecca&country=Saudi Arabia&method=4"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()['data']['date']['hijri']
    except:
        pass
    return None

def get_azkar(category):
    global azkar_data
    if not azkar_data:
        load_azkar()
    
    if azkar_data:
        category_map = {
            'morning': 'أذكار الصباح',
            'evening': 'أذكار المساء',
            'sleep': 'أذكار النوم',
            'prayer': 'أذكار بعد السلام من الصلاة المفروضة',
            'food': 'أذكار الطعام',
            'general': 'تسابيح'
        }
        
        target = category_map.get(category, category)
        for section in azkar_data:
            if target in section.get('category', ''):
                return section.get('array', [])[:10]
    return None

def send_audio_message(chat_id, audio_url, title=""):
    try:
        response = requests.get(audio_url, timeout=60, stream=True)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                temp_path = f.name
            
            with open(temp_path, 'rb') as audio:
                bot.send_audio(chat_id, audio, title=title)
            
            os.remove(temp_path)
            return True
    except:
        pass
    return False

@bot.message_handler(commands=['start'])
def start_command(message):
    welcome_text = """
🌙 *أهلاً بك في بوت رمضان المبارك* 🌙

✨ بوت شامل للمحتوى الإسلامي بمناسبة شهر رمضان الكريم

*المميزات:*
📖 القرآن الكريم كاملاً مع الصوت
🕌 مواقيت الصلاة لأي مدينة
📿 الأذكار اليومية
🤲 أدعية رمضان
📅 التقويم الهجري
📻 إذاعات القرآن الكريم
🔢 سبحة إلكترونية

*رمضان كريم* 🌙
    """
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
📚 *دليل استخدام البوت:*

/start - بدء البوت
/quran - القرآن الكريم
/prayer - مواقيت الصلاة
/azkar - الأذكار
/dua - أدعية رمضان
/hijri - التقويم الهجري

👨‍💻 للتواصل: @priknm
    """
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown", reply_markup=main_menu_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "main_menu":
        bot.edit_message_text(
            "🌙 *القائمة الرئيسية*\n\nاختر من الأقسام التالية:",
            chat_id, message_id,
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
    
    elif call.data == "quran_menu":
        bot.edit_message_text(
            "📖 *القرآن الكريم*\n\nاختر ما تريد:",
            chat_id, message_id,
            parse_mode="Markdown",
            reply_markup=quran_keyboard()
        )
    
    elif call.data == "random_ayah":
        bot.answer_callback_query(call.id, "جاري جلب آية...")
        ayah = get_random_ayah()
        if ayah:
            user_ayah_audio[chat_id] = ayah.get('audio', '')
            text = f"""
📖 *آية عشوائية*

📜 {ayah['text']}

📍 *السورة:* {ayah['surah_ar']}
🔢 *رقم الآية:* {ayah['ayah_num']}
            """
            markup = InlineKeyboardMarkup(row_width=2)
            buttons = [
                InlineKeyboardButton("🎲 آية أخرى", callback_data="random_ayah"),
                InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")
            ]
            if ayah.get('audio'):
                buttons.insert(0, InlineKeyboardButton("🔊 استماع", callback_data="play_ayah_audio"))
            markup.add(*buttons)
            bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "حدث خطأ، حاول مرة أخرى", show_alert=True)
    
    elif call.data == "play_ayah_audio":
        audio_url = user_ayah_audio.get(chat_id)
        if audio_url:
            bot.answer_callback_query(call.id, "جاري إرسال الصوت...")
            success = send_audio_message(chat_id, audio_url, "تلاوة الآية")
            if not success:
                bot.send_message(chat_id, "❌ حدث خطأ في تحميل الصوت")
        else:
            bot.answer_callback_query(call.id, "لا يوجد صوت متاح", show_alert=True)
    
    elif call.data == "surah_list":
        bot.edit_message_text(
            "📋 *قائمة سور القرآن الكريم*\n\nاختر سورة:",
            chat_id, message_id,
            parse_mode="Markdown",
            reply_markup=surah_list_keyboard(0)
        )
    
    elif call.data.startswith("surah_page_"):
        page = int(call.data.split("_")[2])
        bot.edit_message_text(
            "📋 *قائمة سور القرآن الكريم*\n\nاختر سورة:",
            chat_id, message_id,
            parse_mode="Markdown",
            reply_markup=surah_list_keyboard(page)
        )
    
    elif call.data.startswith("surah_") and "page" not in call.data:
        surah_num = int(call.data.split("_")[1])
        bot.answer_callback_query(call.id, "جاري جلب السورة...")
        surah = get_surah(surah_num)
        if surah:
            ayahs_text = "\n\n".join([f"﴿{a['numberInSurah']}﴾ {a['text']}" for a in surah['ayahs'][:10]])
            text = f"""
📖 *سورة {surah['name']}*

📍 نوع السورة: {"مكية" if surah['revelationType'] == "Meccan" else "مدنية"}
🔢 عدد الآيات: {surah['numberOfAyahs']}

{ayahs_text}

{"..." if len(surah['ayahs']) > 10 else ""}
            """
            
            if surah['ayahs'] and surah['ayahs'][0].get('audio'):
                user_ayah_audio[chat_id] = surah['ayahs'][0]['audio']
            
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("🔊 استماع للسورة", callback_data="play_ayah_audio"),
                InlineKeyboardButton("🔙 رجوع للسور", callback_data="surah_list"),
                InlineKeyboardButton("🏠 الرئيسية", callback_data="main_menu")
            )
            bot.edit_message_text(text[:4000], chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "حدث خطأ", show_alert=True)
    
    elif call.data == "surah_by_number":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(chat_id, "📝 أرسل رقم السورة (1-114):")
        bot.register_next_step_handler(msg, process_surah_number)
    
    elif call.data == "search_quran":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(chat_id, "🔍 أرسل كلمة للبحث عنها في القرآن:")
        bot.register_next_step_handler(msg, process_quran_search)
    
    elif call.data == "azkar_menu":
        bot.edit_message_text(
            "📿 *الأذكار*\n\nاختر نوع الأذكار:",
            chat_id, message_id,
            parse_mode="Markdown",
            reply_markup=azkar_keyboard()
        )
    
    elif call.data.startswith("azkar_"):
        category = call.data.replace("azkar_", "")
        category_names = {
            'morning': 'الصباح',
            'evening': 'المساء',
            'sleep': 'النوم',
            'prayer': 'الصلاة',
            'food': 'الطعام',
            'general': 'متنوعة'
        }
        
        bot.answer_callback_query(call.id, "جاري جلب الأذكار...")
        azkar = get_azkar(category)
        
        if azkar and len(azkar) > 0:
            text = f"📿 *أذكار {category_names.get(category, category)}*\n\n"
            for i, zikr in enumerate(azkar[:5], 1):
                if isinstance(zikr, dict):
                    zikr_text = zikr.get('text', '')
                    count = zikr.get('count', '')
                    if count:
                        text += f"*{i}.* {zikr_text[:300]}\n🔄 *التكرار:* {count}\n\n"
                    else:
                        text += f"*{i}.* {zikr_text[:300]}\n\n"
                else:
                    text += f"*{i}.* {str(zikr)[:300]}\n\n"
            
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("🔙 رجوع", callback_data="azkar_menu")
            )
            bot.edit_message_text(text[:4000], chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id, "لا تتوفر أذكار حالياً", show_alert=True)
    
    elif call.data == "prayer_menu":
        text = """
🕌 *مواقيت الصلاة*

اضغط على الزر أدناه ثم أرسل اسم مدينتك
        """
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=prayer_keyboard())
    
    elif call.data == "enter_city":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(chat_id, "📍 أرسل اسم مدينتك (مثال: الرياض أو Cairo):")
        bot.register_next_step_handler(msg, process_city)
    
    elif call.data == "hijri_date":
        bot.answer_callback_query(call.id, "جاري جلب التاريخ...")
        hijri = get_hijri_date()
        if hijri:
            text = f"""
📅 *التقويم الهجري*

🌙 *التاريخ الهجري:*
{hijri['day']} {hijri['month']['ar']} {hijri['year']} هـ

📆 *التاريخ الميلادي:*
{datetime.now().strftime("%d / %m / %Y")}

🗓 *اليوم:* {hijri['weekday']['ar']}

🌟 *الشهر الهجري:* {hijri['month']['ar']}
            """
            bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=back_button())
        else:
            bot.answer_callback_query(call.id, "حدث خطأ في جلب التاريخ", show_alert=True)
    
    elif call.data == "ramadan_duas":
        bot.edit_message_text(
            "🤲 *أدعية رمضان*\n\nاختر الدعاء:",
            chat_id, message_id,
            parse_mode="Markdown",
            reply_markup=ramadan_keyboard()
        )
    
    elif call.data == "dua_iftar":
        text = """
🌙 *دعاء الإفطار*

بِسْمِ اللَّهِ

اللَّهُمَّ لَكَ صُمْتُ وَعَلَى رِزْقِكَ أَفْطَرْتُ

ذَهَبَ الظَّمَأُ وَابْتَلَّتِ الْعُرُوقُ وَثَبَتَ الأَجْرُ إِنْ شَاءَ اللَّهُ

اللَّهُمَّ إِنِّي أَسْأَلُكَ بِرَحْمَتِكَ الَّتِي وَسِعَتْ كُلَّ شَيْءٍ أَنْ تَغْفِرَ لِي
        """
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="ramadan_duas"))
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
    
    elif call.data == "dua_suhoor":
        text = """
🍽 *دعاء السحور*

بِسْمِ اللَّهِ وَعَلَى بَرَكَةِ اللَّهِ

نَوَيْتُ صَوْمَ غَدٍ عَنْ أَدَاءِ فَرْضِ شَهْرِ رَمَضَانَ هَذِهِ السَّنَةِ لِلَّهِ تَعَالَى

اللَّهُمَّ إِنِّي أَسْأَلُكَ بِفَضْلِكَ وَرَحْمَتِكَ أَنْ تُبَارِكَ لِي فِي سَحُورِي

اللَّهُمَّ أَعِنِّي عَلَى صِيَامِهِ وَقِيَامِهِ
        """
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="ramadan_duas"))
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
    
    elif call.data == "dua_laylat_qadr":
        text = """
✨ *دعاء ليلة القدر*

اللَّهُمَّ إِنَّكَ عَفُوٌّ كَرِيمٌ تُحِبُّ الْعَفْوَ فَاعْفُ عَنِّي

اللَّهُمَّ إِنِّي أَسْأَلُكَ الْجَنَّةَ وَمَا قَرَّبَ إِلَيْهَا مِنْ قَوْلٍ أَوْ عَمَلٍ

وَأَعُوذُ بِكَ مِنَ النَّارِ وَمَا قَرَّبَ إِلَيْهَا مِنْ قَوْلٍ أَوْ عَمَلٍ

*قال رسول الله ﷺ:*
تَحَرَّوْا لَيْلَةَ الْقَدْرِ فِي الْعَشْرِ الأَوَاخِرِ مِنْ رَمَضَانَ
        """
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="ramadan_duas"))
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
    
    elif call.data == "dua_fasting":
        text = """
🤲 *أدعية الصيام*

*1. عند الإفطار:*
ذَهَبَ الظَّمَأُ وَابْتَلَّتِ الْعُرُوقُ وَثَبَتَ الأَجْرُ إِنْ شَاءَ اللَّهُ

*2. عند السحور:*
اللَّهُمَّ بَارِكْ لَنَا فِيمَا رَزَقْتَنَا وَقِنَا عَذَابَ النَّارِ

*3. للصائم إذا أفطر عند قوم:*
أَفْطَرَ عِنْدَكُمُ الصَّائِمُونَ وَأَكَلَ طَعَامَكُمُ الأَبْرَارُ وَصَلَّتْ عَلَيْكُمُ الْمَلائِكَةُ

*4. إذا شُتم الصائم:*
إِنِّي صَائِمٌ، إِنِّي صَائِمٌ
        """
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔙 رجوع", callback_data="ramadan_duas"))
        bot.edit_message_text(text, chat_id, message_id, parse_mode="Markdown", reply_markup=markup)
    
    elif call.data == "ramadan_khatma":
        hijri = get_hijri_date()
        if hijri:
            try:
                day = int(hijri['day'])
                month = hijri['month']['ar']
                
                if 'رمضان' in month or 'Ramadan' in month.lower():
                    start_page = ((day - 1) * 20) + 1
                    end_page = min(day * 20, 604)
                    progress = min(day * 100 // 30, 100)
                    
                    text = f"""
📖 *ختمة رمضان*

🌙 *اليوم:* {day} {month}

📑 *ورد اليوم:*
من صفحة {start_page} إلى صفحة {end_page}

📊 *الت
