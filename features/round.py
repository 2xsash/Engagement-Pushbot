
from config import *
import concurrent.futures

def checklist_round(message, user_id):
    text = f"""
In 10 Minuten Endet die aktuelle Runde ⚠️ Bitte check nochmal, ob du die Liste abgearbeitet hast
    """
    bot.send_message(
        chat_id=user_id,
        text=text
    )

def endof_round(message, user_id):
    text = f"""
Die Runde ist vorbei, die nächste Runde ist um 20:00 ⏱
    """
    bot.send_message(
        chat_id=user_id,
        text=text
    )

def start_round(message, user_id):
    print("MESSAGE________________________+++++++++++++++++++++++++++", message.message_id)
    # user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    roundlast = db.Rounds.get_lastRound()
    round_id = roundlast.id
    users = db.Users.get_ids()
    message_id = message.message_id + users.index(user_id)
    drop_duration = roundlast.drop_duration()
    end_round = (roundlast.end()-datetime.datetime.now()).total_seconds()
    text = f"""
Die Runde ist gestartet ✅
"""
    bot.send_message(
        # text,
        # chat_id=user_id,
        # message_id=message_id,
        # parse_mode="html"
        
        chat_id=user_id,
        text=text
    )
    # gets registered member list and send list to user to like
    def listToString(s):
        str1 = """"""
        for ele in s:
            str1 += (ele+"""
""")
        return str1

    round_current = db.Rounds.get_round(round_id)
    member_list = [i.user_id for i in round_current.memberlist]
    member_list_insta = ["https://www.instagram.com/"+i.username for i in round_current.memberlist]
    member_list_string = listToString(member_list_insta)

    if epush_user.user_id in member_list:
# sends list of registered members to all registered memebers
        text = f"""
Please follow all Engagement instructions
        """
        list_text = f"""
Die Runde ist gestartet - hier ist die Liste. Bitte von allen Accounts den neuesten Post liken und einen regelkonformen Kommentar hinterlassen❤️

{member_list_string}

"""
        bot.send_message(
            chat_id=user_id,
            text=list_text,
            parse_mode="html"
        )
    else:
# Missed the round
        text = f"""
Du hast die aktuelle Runde leider verpasst 😫
    """
        bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode="html"
        )


@bot.message_handler(commands=["round"])
def round_func(message):
    user_id = message.from_user.id
    epush_user = db.Users.get(user_id)
    users = db.Users.get_ids()
    round_start = db.Rounds.create_now()
    drop_duration = round_start.drop_duration()
    check_time = round_start.check_time()
    endtime = round_start.end()
    print("starting...")
    ##this creates a new thread
    text=f"""
Die nächste Engagement-Runde startet in <b>{drop_duration} seconds</b> ⏳. Wenn
du daran teilnehmen möchtest, drücke einfach auf den Button 💁🏽🏽♀
    """
    btn_text=f"Runde mit @{epush_user.username} beitreten."
    usern_mrkp = telebot.types.InlineKeyboardMarkup()
    usern_btn = telebot.types.InlineKeyboardButton(text=btn_text, callback_data="join_round")
    usern_mrkp.add(usern_btn)

# creates the scheduler and schedules task
    scheduler = BackgroundScheduler()
    timer = datetime.datetime.now() + datetime.timedelta(seconds=drop_duration)
    @scheduler.scheduled_job("date", id="schedsetter", run_date=timer, args=[message, users])
    def sched_start_round(message, users):
        for user_id in users:
            print("start round")
            round_thread = threading.Timer(1,start_round,args=[message, user_id])
            round_thread.name= "round_thread"
            round_thread.start()

    @scheduler.scheduled_job("date", id="checklist", run_date=check_time, args=[message, users])
    def check_time(message, users):
        print("checking time")
        roundlast = db.Rounds.get_lastRound()
        round_id = roundlast.id
        round_current = db.Rounds.get_round(round_id)
        member_list = [i.user_id for i in round_current.memberlist]
        for user_id in member_list:
            round_thread = threading.Timer(1,checklist_round,args=[message, user_id])
            round_thread.name= "checklist_thread"
            round_thread.start()

    @scheduler.scheduled_job("date", id="endoftime", run_date=endtime, args=[message, users])
    def endof_time(message, users):
        print("end of time")
        for user_id in users:
            round_thread = threading.Timer(1,endof_round,args=[message, user_id])
            round_thread.name= "endof_thread"
            round_thread.start()

    scheduler.start()

# messages every user of the round starting in xminutes
    def start_round_thread(user_id):
        user=db.Users.get(user_id)
        btn_text=f"Runde mit @{user.username} beitreten."
        usern_mrkp = telebot.types.InlineKeyboardMarkup()
        usern_btn = telebot.types.InlineKeyboardButton(text=btn_text, callback_data="join_round")
        usern_mrkp.add(usern_btn)
        
        bot.send_message(
            user_id,
            text=text,
            reply_markup=usern_mrkp,
            parse_mode="html"
        )
    for user_id in users:
        start_round_thread(user_id)

#### ROUND CALLBACK

@bot.callback_query_handler(func=lambda call: call.data=="join_round")
def join_round(call):   
    user_id = call.from_user.id
    message_id = call.message.message_id
    epush_user = db.Users.get(user_id)
    round_started = db.Rounds.get_lastRound()
    if epush_user.warns>=3:
        text = f"""Sorry you can't join round, you've been blocked
🔴Contact support🔴
"""
        bot.send_message(
            user_id,
            text=text,
            parse_mode="html"
        )
    else:
        if round_started.drop_duration():
            round_started.join(epush_user)
            time_left = round_started.drop_duration()
            #TODO remove pause here
            # run_sched(user_id, 20)
            text = f"""Du bist nun für die nächste Runde registriert♻️
    """
            bot.send_message(
                user_id,
                text=text,
                parse_mode="html"
            )
            # bot.edit_message_text(
            #     text,
            #     chat_id=user_id,
            #     message_id=message_id,
            #     parse_mode="html"
            # )
        else:
            text = f"""Oopps drop session for the last round has ended
the next round starts in 1hour, be sure not to miss it"""
            bot.send_message(
                user_id,
                text=text,
                parse_mode="html"
            )


