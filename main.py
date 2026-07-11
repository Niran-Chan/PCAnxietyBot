from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os 
import psutil
from time import sleep
import asyncio

load_dotenv() 
API_KEY=os.getenv("API_KEY")
IS_START = False

whitelist = os.getenv("WHITELIST_TELEID")
if(whitelist):
    whitelist = whitelist.strip().split(",")
def get_status() -> dict:
    results = {
        "CPU,%" : None,
        "Temperature,°C" : None,
        "Memory" : {
            "Total": None,
            "Available": None,
            "Used" : None,
            "Percent": None
        }
    }
    cpu_percent = psutil.cpu_percent(interval=None,percpu=True)
    results["CPU,%"] = cpu_percent

    #Memory
    mem = psutil.virtual_memory()
    results["Memory"]["Total"] = mem.total
    results["Memory"]["Available"] =  mem.available
    results["Memory"]["Used"] =  mem.used
    results["Memory"]["Percent"] = mem.percent
    
    #Temperature

    try:
        temps = psutil.sensors_temperatures()
        results["Temperature,°C"] = temps
    
    except Exception:
        pass

    return results

async def start(update: Update,context: ContextTypes.DEFAULT_TYPE)->None:
    user_id = str(update.effective_user.id)
    if user_id not in whitelist:
        return 
    await update.message.reply_text(f"Hi! I am PCAnxietyBot. I am here to help you with your anxious needs by reassuring you about the status of your pc every hour right here. Lets get started!")
    #user_id = update.effective_user.id
    #await update.message.reply_text(f"Your Telegram UserID is : {update.effective_user.id}")

    global IS_START
    IS_START = True
    while(IS_START):
        status = get_status()
        formatted_str = "\n".join(f"{key:<20} {val}" for key, val in status.items())
        await update.message.reply_text(
        f"```\n{formatted_str}\n```",
        parse_mode="MarkdownV2")
        await asyncio.sleep(3)
        break
    return

async def stop(update: Update,context: ContextTypes.DEFAULT_TYPE):
    global IS_START
    IS_START = False
    return 

def run():
    app = ApplicationBuilder().token(API_KEY).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == '__main__':
    run()