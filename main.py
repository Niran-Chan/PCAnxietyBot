from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os 
import psutil

load_dotenv() 
API_KEY=os.getenv("API_KEY")
IS_START = True


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
    await update.message.reply_text(f"Hi! I am PCAnxietyBot. I am here to help you with your anxious needs by reassuring you about the status of your pc every hour right here. Lets get started!")
    status = get_status()
    formatted_str = "\n".join(f"{key:<20} {val}" for key, val in status.items())
    await update.message.reply_text(
    f"```\n{formatted_str}\n```",
    parse_mode="MarkdownV2"
)




app = ApplicationBuilder().token(API_KEY).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()