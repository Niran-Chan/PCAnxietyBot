from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
import os 
import psutil
from time import sleep
import asyncio
from pynvml import *

load_dotenv() 
API_KEY=os.getenv("API_KEY")
status_task = None

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
        },
        "GPU" : None
    }
    while True:
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
        
        #GPU
        try:
            nvmlInit()
            count = nvmlDeviceGetCount()

            for i in range(count):
                handle = nvmlDeviceGetHandleByIndex(i)
                print(nvmlDeviceGetName(handle))
                util = nvmlDeviceGetUtilizationRates(handle)

                #print(util.gpu)      # %
                #print(util.memory)   # %
                key = nvmlDeviceGetName(handle).decode()
                results[key]["Utilisation,%"] = util
                
                mem = nvmlDeviceGetMemoryInfo(handle)
                results[key]["Memory"] = mem

                #Temperature
                temp = nvmlDeviceGetTemperature(handle,NVML_TEMPERATURE_GPU)
                results[key]["Temperature,°C"] = temp
            nvmlShutdown()
        
        except Exception:
            pass
        
        return results
        

async def send_status(chat_id, bot):
    while True:
        status = get_status()
        formatted = "\n".join(f"{k:<20} {v}"for k, v in status.items())

        await bot.send_message(
            chat_id,
            f"```\n{formatted}\n```",
            parse_mode="MarkdownV2",
        )

        await asyncio.sleep(3)  

async def start(update: Update,context: ContextTypes.DEFAULT_TYPE)->None:
    
    user_id = str(update.effective_user.id)
    if user_id not in whitelist:
        return 
    
    global status_task
    if status_task is None or status_task.done():
        await update.message.reply_text(f"Hi! I am PCAnxietyBot. I am here to help you with your anxious needs by reassuring you about the status of your pc every hour right here. Lets get started!")
        #user_id = update.effective_user.id
        #await update.message.reply_text(f"Your Telegram UserID is : {update.effective_user.id}")
        status_task = asyncio.create_task(send_status(user_id,context.bot))

async def stop(update: Update,context: ContextTypes.DEFAULT_TYPE):
    global status_task
    #print("Attempting to stop")
    if status_task:
        status_task.cancel()
        status_task = None

    await update.message.reply_text("Monitoring stopped. Please /start again to start your hourly update")

def run():
    app = ApplicationBuilder().token(API_KEY).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.run_polling()

if __name__ == '__main__':
    run()