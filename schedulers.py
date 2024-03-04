from Sheet.sheetAPI import SheetAPI
from Parser.parser import parser_run
from secondary_functions import sort_arrays
import schedule
import time
import pytz
from datetime import datetime


def task():
    try:
        print(f"Data update => START : DATA {datetime.now()}")
        tab_ids = [
            '',
            '',
            '',
            ''
        ]
        for tab_id in tab_ids:
            tb = SheetAPI(tab_id)
            sku = tb.read("", "")
            links = tb.read("", "")
            result = parser_run(links, sku)
            data, variation = sort_arrays(result, sku)
            print(tb.write("", "", data))
            print(tb.write("", "", variation))
        print('Task => SUCCESSFULLY')
    except:
        print('Task => ERROR')


def schedule_tasks():
    print("Script run...")
    kyiv_timezone = pytz.timezone("Europe/Kiev")
    schedule.tz = kyiv_timezone
    schedule.every().day.at("03:00").do(task)
    schedule.every().day.at("12:00").do(task)

    while True:
        schedule.run_pending()
        time.sleep(1)

