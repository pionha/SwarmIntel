import os
import time
from argparse import ArgumentParser
from collections import deque

from dotenv import load_dotenv
from tqdm import tqdm
from web3 import Web3

# --- Цветовые константы для красивого вывода ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_eth_connection():
    """Устанавливает соединение с Ethereum нодой через Infura."""
    load_dotenv()
    infura_project_id = os.getenv("INFURA_PROJECT_ID")
    if not infura_project_id or infura_project_id == "YOUR_INFURA_PROJECT_ID_HERE":
        print(f"{Colors.FAIL}Ошибка: INFURA_PROJECT_ID не найден.{Colors.ENDC}")
        print(f"Пожалуйста, создайте файл {Colors.BOLD}.env{Colors.ENDC} и добавьте в него ваш ключ.")
        print("Пример: INFURA_PROJECT_ID=\"abcdef1234567890\"")
        return None
    
    w3 = Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{infura_project_id}'))
    
    if not w3.is_connected():
        print(f"{Colors.FAIL}Не удалось подключиться к Ethereum Mainnet.{Colors.ENDC}")
        return None
        
    print(f"{Colors.GREEN}Успешно подключено к Ethereum Mainnet.{Colors.ENDC}")
    return w3

def track_momentum(w3, contract_address, num_blocks):
    """
    Анализирует моментум роста сообщества вокруг смарт-контракта.
    Основная метрика - скорость появления новых уникальных адресов.
    """
    try:
        target_address = w3.to_checksum_address(contract_address)
    except ValueError:
        print(f"{Colors.FAIL}Ошибка: Неверный формат адреса контракта.{Colors.ENDC}")
        return

    latest_block_number = w3.eth.block_number
    start_block = latest_block_number - num_blocks + 1

    print(f"\n{Colors.HEADER}{Colors.BOLD}🐝 Запуск SwarmIntel... Сбор данных о рое.{Colors.ENDC}")
    print(f"🎯 {Colors.CYAN}Целевой контракт:{Colors.ENDC} {target_address}")
    print(f" SCANNING_DEPTH  SCANNING_DEPTH_IN_BLOCKS{Colors.CYAN}Глубина анализа:{Colors.ENDC} {num_blocks} блоков (с {start_block} по {latest_block_number})")
    
    period_unique_interactors = set()
    period_transactions = 0

    pbar = tqdm(range(start_block, latest_block_number + 1), 
                desc=f"{Colors.BLUE}Отслеживание блоков{Colors.ENDC}",
                ncols=100)

    for block_num in pbar:
        try:
            block = w3.eth.get_block(block_num, full_transactions=True)
            for tx in block.transactions:
                if tx['to'] and w3.to_checksum_address(tx['to']) == target_address:
                    period_transactions += 1
                    from_address = w3.to_checksum_address(tx['from'])
                    period_unique_interactors.add(from_address)
        except Exception as e:
            tqdm.write(f"{Colors.WARNING}Не удалось обработать блок {block_num}: {e}{Colors.ENDC}")
            continue

    # --- ВЫЧИСЛЕНИЕ МЕТРИК ---
    total_unique_wallets = len(period_unique_interactors)
    
    # Симулируем, что до этого периода мы не знали ни об одном кошельке.
    # В реальном приложении здесь было бы сравнение с базой данных "старых" кошельков.
    known_wallets_before_period = set() 
    new_wallets = period_unique_interactors - known_wallets_before_period
    
    # Наша ключевая метрика!
    growth_momentum_index = (len(new_wallets) / total_unique_wallets) * 100 if total_unique_wallets > 0 else 0

    # --- ВЫВОД РЕЗУЛЬТАТОВ ---
    print(f"\n{Colors.HEADER}{Colors.BOLD}📊 Результаты анализа моментума:{Colors.ENDC}")
    print("-" * 55)
    print(f"Общее число транзакций за период: {Colors.BOLD}{Colors.GREEN}{period_transactions}{Colors.ENDC}")
    print(f"Участников роя (уникальных кошельков): {Colors.BOLD}{Colors.GREEN}{total_unique_wallets}{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}{Colors.UNDERLINE}Ключевая метрика SwarmIntel:{Colors.ENDC}")
    print(f"📈 {Colors.WARNING}Индекс Моментума Роста (Growth Momentum Index):{Colors.ENDC} "
          f"{Colors.BOLD}{growth_momentum_index:.2f}%{Colors.ENDC}")
    print(f"   {Colors.WARNING}(Доля новых участников в общей активности роя){Colors.ENDC}")
    print("-" * 55)
    
    if growth_momentum_index > 80:
         print(f"{Colors.GREEN}ВЫВОД: Гипер-рост! Проект демонстрирует взрывной рост сообщества (эффект роя).{Colors.ENDC}")
    elif growth_momentum_index > 50:
        print(f"{Colors.CYAN}ВЫВОД: Сильный моментум. Наблюдается стабильный и уверенный приток новых пользователей.{Colors.ENDC}")
    else:
        print(f"{Colors.BLUE}ВЫВОД: Умеренный моментум. Активность генерируется в основном ядром сообщества.{Colors.ENDC}")


if __name__ == "__main__":
    parser = ArgumentParser(description="SwarmIntel - отслеживает моментум роста сообщества вокруг смарт-контракта.")
    parser.add_argument("contract", help="Адрес смарт-контракта для анализа.")
    parser.add_argument("-b", "--blocks", type=int, default=1000, help="Количество последних блоков для анализа (по умолчанию: 1000).")
    
    args = parser.parse_args()
    
    web3_connection = get_eth_connection()
    if web3_connection:
        track_momentum(web3_connection, args.contract, args.blocks)
