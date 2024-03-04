import asyncio
import aiohttp
import re
from datetime import datetime
import lxml
from bs4 import BeautifulSoup as BS


class Parser:

    def __init__(self, proxy, semaphore):
        self.proxy = proxy
        self.semaphore = semaphore

    async def parser_procurement_data(self, url: str, id: str):
        try:
            async with self.semaphore:
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                    while True:
                        response = await session.get(url=url, proxy=self.proxy)
                        print(response.status)
                        if response.status == 503:
                            await asyncio.sleep(2)
                        elif response.status == 404:
                            return [id, 0, 0, 0, '0days', 'No-Info', False]
                        else:
                            break
                    soup = BS(await response.text(), 'html.parser')
                    item = []
                    variable = soup.find(class_='x-msku__box-cont')
                    if variable is not None:
                        return [id, 0, 0, 0, '0days', 'Variation True', True]
                    item.append(id)
                    price = soup.select_one('div.x-price-primary span.ux-textspans').text.split('$')[-1]
                    if len(price) > 5:
                        item.append(float(price.split('/')[0]))
                    else:
                        item.append(float(price))
                    price_ship = soup.find(class_='ux-labels-values--shipping').find(class_='ux-textspans--BOLD').text
                    if 'Free' in price_ship:
                        item.append(0)
                    else:
                        item.append(float(price_ship.split('$')[-1]))
                    script_blocks = soup.find_all('script')
                    input_str = [str(tag) for tag in script_blocks]
                    start_text_stok = '"maxValue":"'
                    end_text_stok = '"'
                    pattern = re.compile(f'{re.escape(start_text_stok)}(.*?){re.escape(end_text_stok)}')
                    match = pattern.search(''.join(input_str))
                    if match:
                        result_string = match.group(1)
                        item.append(result_string)
                    else:
                        item.append(0)
                    delivery_days = soup.find(class_='ux-labels-values--deliverto')
                    if delivery_days is None:
                        delivery_days = soup.find(class_='ux-labels-values__values col-9').find_all(
                            class_='ux-textspans--BOLD')
                    else:
                        delivery_days = delivery_days.find_all(class_='ux-textspans--BOLD')
                    if len(delivery_days) > 1:
                        try:
                            date_text = delivery_days[-1].text
                            target_date = datetime.strptime(date_text, '%a, %b %d')
                            target_date = target_date.replace(year=2024)
                            current_date = datetime.now()
                            difference = target_date - current_date
                            item.append(f"{difference.days + 1}days")
                        except:
                            date_text = delivery_days[1].text
                            target_date = datetime.strptime(date_text, '%a, %b %d')
                            target_date = target_date.replace(year=2024)
                            current_date = datetime.now()
                            difference = target_date - current_date
                            item.append(f"{difference.days + 1}days")
                    else:
                        item.append('ERROR')
                    suppliers = soup.find(class_='x-sellercard-atf__info').find(
                        class_='ux-textspans ux-textspans--BOLD').text
                    item.append(suppliers)
                    item.append(False)
                    return item
        except Exception as e:
            print(f"Error: {e}")
            print(url)
            return [id, 0, 0, 0, '0days', f'Ended', False]


async def run_parsers(list_of_urls: list, list_ids: list):
    semaphore = asyncio.Semaphore(10)
    proxy = ''
    parser = Parser(proxy, semaphore)
    tasks = [(asyncio.create_task(parser.parser_procurement_data(url, ID))) for (url, ID) in zip(list_of_urls, list_ids)]
    result = await asyncio.gather(*tasks)
    return result


def parser_run(list_of_urls: list, list_ids: list):
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(run_parsers(list_of_urls, list_ids))
    return results


if __name__ == '__main__':
    print('The is parser.')
