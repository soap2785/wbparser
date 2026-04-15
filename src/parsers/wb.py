from asyncio import sleep as asleep

from playwright.async_api import Locator

from base_methods import BaseMethods
from schemas import RequestPayload
from enums import ParserType
from .local_cons import WB_URL, PHOTOS_LIMIT, LIMIT


class WB(BaseMethods):
    @classmethod
    async def check(cls, req: RequestPayload) -> None:
        cls.Info(ParserType.WB, 1)
        page = req.browser.pages[0]
        await page.goto(WB_URL, wait_until="domcontentloaded")

        await asleep(2)
        await page.click("#searchInput")
        await page.type("#searchInput", req.query["main"])
        await page.press("#searchInput", "Enter")
        await asleep(2)
        await page.locator(".dropdown-filter__btn").nth(1).click()
        await asleep(1)
        if req.query.get("price"):
            await page.locator(".j-range").nth(1).fill(str(req.query.get("price")))
        if req.query.get("origin"):
            for variant in await page.locator(".filter").nth(22).locator("li").all():
                if await variant.locator(".checkbox-with-text__text").inner_text() == req.query.get("origin"):
                    await variant.locator(".checkbox-with-text__decor").click()
                    break
        await page.get_by_role("button", name="Показать", exact=True).click()
        await asleep(1)
        results = []
        for idx, product in enumerate(await page.locator(".product-card").all()):
            if idx > LIMIT:
                break
            if req.query.get("rating"):
                if float((await product.locator(".address-rate-mini").inner_text()).replace(",", ".")) <= float((req.query.get("rating")).replace(",", ".")):
                    continue
            for _ in range(5):
                rawarticle = await product.get_attribute("id")
                if article := rawarticle[1:] if rawarticle else None:
                    # data about product from home page
                    result = {
                        "Ссылка на товар": await product.locator(".product-card__link").get_attribute("href"),
                        "Артикул": article,
                        "Название товара": (await product.locator(".product-card__name").inner_text()).replace("/ ", "").replace("/", ""),
                        "Цена": (await product.locator(".price__lower-price").inner_text()).replace('\xa0', '').replace('₽', '').strip(),
                    }

                    # description
                    new_page = await req.browser.new_page()
                    await new_page.goto(result["Ссылка на товар"], wait_until="domcontentloaded")
                    await asleep(4)
                    await new_page.get_by_role("button", name="Характеристики и описание").click()
                    await asleep(1)
                    result["Описание"] = await new_page.locator("#section-description").locator(".mo-typography_variant_description").inner_text()
                    await asleep(1)
                    await new_page.click("body")
                    await asleep(1)

                    # photos
                    photos = ""
                    i = 1
                    for _ in range(PHOTOS_LIMIT):
                        if await new_page.get_by_test_id("activeVideo").count() > 0:
                            break
                        try:
                            photos = photos + await new_page.get_by_test_id("activeMainPhoto").get_by_role("img", name=f"Product image {i}", exact=True).get_attribute("src") + ","
                        except Exception:  # reached end of photos
                            break
                        await asleep(0.5)
                        await new_page.get_by_label("Следующее фото").click()
                        i += 1
                    result["Фото"] = photos

                    # structured characteristics
                    await new_page.get_by_role("button", name="Характеристики и описание").click()
                    tbodies: list[Locator] = [tbody for tbody in await new_page.get_by_test_id("product_additional_information").locator("tbody").all()]
                    main_data: list[Locator] = await tbodies[0].locator("tr").all()
                    sub_data: list[Locator] = await tbodies[1].locator("tr").all()
                    
                    async def GetKeyFromTableRow(table_row: Locator) -> str:
                        return await table_row.locator(".mo-typography_color_secondary").inner_text()

                    async def GetValueFromTableRow(table_row: Locator) -> str:
                        return await table_row.locator(".mo-typography_color_primary").inner_text()                    

                    result["Характеристики"] = {
                        "Основная ифнормация": {
                            await GetKeyFromTableRow(main_data[i]): await GetValueFromTableRow(main_data[i])
                            for i in range(len(main_data))
                        },
                        "Дополнительная информация": {
                            await GetKeyFromTableRow(sub_data[i]): await GetValueFromTableRow(sub_data[i])
                            for i in range(len(sub_data))
                        }
                    }
                    await asleep(1)
                    await new_page.click("body")

                    # seller name and link
                    seller = new_page.get_by_label("Подробнее о продавце")
                    result["Название селлера"] = await seller.locator(".mo-typography").nth(1).inner_text()
                    result["Ссылка на селлера"] = f"{WB_URL.replace(".ru/", ".ru")}{await seller.get_attribute("href")}"

                    await asleep(1)
                    # sizes of product
                    result["Размеры товара"] = ""
                    try:
                        await new_page.get_by_role("button", name="Ещё").click(force=True, timeout=5000)
                    except Exception:  # Button "Ещё" doesn't exist
                        pass
                    await new_page.click("body")
                    for size in await new_page.get_by_test_id("cardtype:colors").locator("ul").locator("li").all():
                        try:
                            international = await size.locator(".mo-typography_color_primary").inner_text(timeout=5000)
                            russian = await size.locator(".mo-typography_color_secondary").inner_text(timeout=5000)
                            result["Размеры товара"] = result["Размеры товара"] + f"{international}:{russian},"
                        except Exception:
                            break

                    # I haven't found this information, maybe it's an ozon feature?
                    # remaining products
                    result["Остаток по товару"] = "Данные не обнаружены"
                    result["Рейтинг"] = await product.locator(".address-rate-mini").inner_text()
                    result["Количество отзывов"] = await product.locator(".address-rate-mini").inner_text()
                    await new_page.close()
                    results.append(result)
                    break
                else:
                    continue
            req.response.wb = results
        cls.Info(ParserType.WB, 2)
