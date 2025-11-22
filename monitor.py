# monitor.py
import asyncio
import aiohttp
import time
from database import save_result, get_last_checks
import argparse

# Ограничение на количество одновременных запросов
CONCURRENCY_LIMIT = 20


async def check_url(session, url):
    """Асинхронно проверяет один URL."""
    start_time = time.monotonic()
    status_code = 0

    try:
        # Использование context manager 'async with' для сессии
        async with session.get(url, timeout=10) as response:
            status_code = response.status
            is_success = 1 if 200 <= status_code < 400 else 0

    except aiohttp.client_exceptions.ClientConnectorError:
        status_code = 999  # Ошибка соединения
        is_success = 0
    except asyncio.TimeoutError:
        status_code = 998  # Таймаут
        is_success = 0
    except Exception as e:
        status_code = 997  # Другие ошибки
        is_success = 0

    response_time = time.monotonic() - start_time

    # Сохранение результата в БД (работа с БД синхронна, но выполняется быстро)
    save_result(url, status_code, response_time, is_success)

    status_color = "\033[92m" if is_success else "\033[91m"
    print(f"{status_color}[{status_code}] {url} | Время: {response_time:.2f} сек.\033[0m")

    return url, status_code, response_time

async def run_checks(urls):
    """Запускает асинхронные проверки для всех URL."""

    # Создаем асинхронную сессию
    async with aiohttp.ClientSession() as session:
        # Создаем список задач (tasks)
        tasks = [check_url(session, url) for url in urls]

        print(f"\n🚀 Запуск асинхронной проверки {len(urls)} сайтов...")

        # Запускаем все задачи и ждем их выполнения
        await asyncio.gather(*tasks)


def get_urls_from_file(filename="urls.txt"):
    """Читает список URL из файла."""
    try:
        with open(filename, 'r') as f:
            # Очищаем от лишних пробелов и пустых строк
            urls = [line.strip() for line in f if line.strip()]
        return urls
    except FileNotFoundError:
        print(f"❌ Файл {filename} не найден. Создайте его и добавьте URL.")
        return []


def display_history():
    """Выводит историю последних проверок."""
    results = get_last_checks(limit=15)

    if not results:
        print("Истории проверок пока нет.")
        return

    print("\n--- 📜 Последние Результаты Проверок ---")
    for r in results:
        status_color = "\033[92m" if r.is_success else "\033[91m"
        print(
            f"{r.timestamp.strftime('%H:%M:%S')} | {status_color}[{r.status_code}] {r.url[:40]}... | {r.response_time:.2f} с.\033[0m")
    print("------------------------------------------")


