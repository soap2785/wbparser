import argparse
from asyncio import run
import os

import pandas as pd
from playwright_stealth.stealth import async_api

from namespaces import ResponseData
from schemas import RequestPayload
from parsers.wb import WB
from constants import USER_AGENT

parser = argparse.ArgumentParser()
parser.add_argument("query", help="Поисковый запрос")
parser.add_argument("--rating", help="вкл/откл фильтр по рейтингу от 4.7")
parser.add_argument("--origin", help="страна производства")
parser.add_argument("--price", help="максимальная цена")
args = parser.parse_args()


async def Run(args: argparse.Namespace) -> None:
    query = {
        "main": args.query,
    }
    if args.origin:
        query["origin"] = args.origin
    if args.price:
        query["price"] = args.price
    if args.rating:
        query["rating"] = args.rating
    response = ResponseData()
    async with async_api.async_playwright() as p:
        user_data_dir = os.path.join(os.getcwd(), "user_data")
        browser = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ],
            user_agent=USER_AGENT
        )
        request = RequestPayload(
            query=query,
            browser=browser,
            response=response,
        )
        await WB.check(request)
        if response.wb:
            with pd.ExcelWriter('wb_data_full.xlsx') as writer:
                main_df = pd.json_normalize(response.wb)
                main_df.to_excel(writer, sheet_name='Товары', index=False)

                worksheet = writer.sheets['Товары']

                for row in worksheet.iter_rows():
                    for cell in row:
                        cell.alignment = cell.alignment.copy(wrapText=False)

                for column in worksheet.columns:
                    column_letter = column[0].column_letter
                    worksheet.column_dimensions[column_letter].width = 20

run(Run(args))