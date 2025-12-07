from selenium import webdriver  # импортируем модуль для управления браузером
from selenium.webdriver.common.by import By  # импортируем способы поиска элементов на странице
from selenium.webdriver.support.ui import WebDriverWait  # импортируем класс для явных ожиданий
from selenium.webdriver.support import expected_conditions as EC  # импортируем готовые условия ожидания
from selenium.webdriver.common.keys import Keys  # импортируем виртуальные клавиши (enter, arrows и т.д.)
from selenium.webdriver.common.action_chains import ActionChains  # импортируем для сложных действий мыши/клавиатуры
import time  # импортируем модуль для простых пауз

def setup_driver():  # функция для настройки и запуска Firefox
    options = webdriver.FirefoxOptions()  # создаём объект опций для Firefox
    options.add_argument("--start-maximized")  # запускаем браузер в развернутом окне
    # options.add_argument("--headless")  # если нужно без интерфейса
    driver = webdriver.Firefox(options=options)  # создаём экземпляр WebDriver
    driver.set_page_load_timeout(60)  # устанавливаем таймаут загрузки страницы
    return driver  # возвращаем готовый драйвер

driver = setup_driver()  # запускаем Firefox через функцию
url = 'https://www.onetwotrip.com/'  # URL сайта
driver.get(url)  # открываем сайт
print(f"Перешел на страницу: {url}")  # выводим сообщение

try:
    wait = WebDriverWait(driver, 30)  # создаём явное ожидание (до 30 секунд)

    # --- Поле "Откуда" ---
    from_input = wait.until(  # ждём появления поля "Откуда"
        EC.presence_of_element_located((By.NAME, "flights[0].from"))
    )
    from_input.clear()  # очищаем поле
    from_input.send_keys("Москва")  # вводим текст
    time.sleep(1)  # ждём подгрузку автокомплита

    actions = ActionChains(driver)
    actions.move_to_element(from_input)
    actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    time.sleep(0.5)

    # --- Поле "Куда" ---
    to_input = wait.until(
        EC.presence_of_element_located((By.NAME, "flights[0].to"))
    )
    to_input.clear()
    to_input.send_keys("Санкт-Петербург")
    time.sleep(1)

    actions = ActionChains(driver)
    actions.move_to_element(to_input)
    actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()
    time.sleep(0.5)

    # --- Выбор даты 20 октября ---
    date_20 = wait.until(
        EC.element_to_be_clickable((By.XPATH,
            "//span[text()='20' and ancestor::div[contains(@class,'inner--hasBorderOnHover')]]"))
    )
    date_20.click()
    time.sleep(0.5)

    # --- Кнопка поиска ---
    search_button = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
    )
    driver.execute_script("arguments[0].click();", search_button)

    # --- Ждём появления хотя бы одного билета ---
    timeout = 60
    interval = 1
    elapsed = 0
    tickets = []

    while elapsed < timeout:
        tickets = driver.find_elements(By.CSS_SELECTOR, "div.K-Azu")
        tickets_with_price = []
        for t in tickets:
            try:
                price = t.find_element(By.CSS_SELECTOR, "span.NtDKJ span")
                tickets_with_price.append(t)
            except:
                continue
        if tickets_with_price:
            tickets = tickets_with_price
            break
        time.sleep(interval)
        elapsed += interval

    print(f"Найдено билетов с ценой: {len(tickets)} (выведем топ-5)")

    for ticket in tickets[:5]:
        # --- Авиакомпания ---
        try:
            airline = ticket.find_element(
                By.XPATH,
                ".//div[contains(@class,'OQNeK')]//span[normalize-space(text())!='']"
            ).text
        except:
            airline = "N/A"

        # --- Время и аэропорты ---
        try:
            depart_time = ticket.find_elements(By.CSS_SELECTOR, "div.HZQKF span.y66Vm")[0].text
            depart_airport = ticket.find_elements(By.CSS_SELECTOR, "div.HZQKF div.lT-ju")[0].text
            arrive_time = ticket.find_elements(By.CSS_SELECTOR, "div.HZQKF span.y66Vm")[1].text
            arrive_airport = ticket.find_elements(By.CSS_SELECTOR, "div.HZQKF div.lT-ju")[1].text
        except:
            depart_time = depart_airport = arrive_time = arrive_airport = "N/A"

        # --- Цена ---
        try:
            price = ticket.find_element(By.CSS_SELECTOR, "span.NtDKJ span").text
        except:
            price = "N/A"

        print(f"{airline} | {depart_time}-{arrive_time} | {depart_airport}-{arrive_airport} | {price} ₽")

finally:
    driver.quit()  # закрываем браузер даже при ошибке
