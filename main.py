import os
import sys
from pathlib import Path


def should_ignore(path, ignore_patterns, ignore_hidden=True):
    """
    Проверяет, нужно ли игнорировать файл/папку
    """
    path_str = str(path)
    name = path.name

    # Игнорировать скрытые файлы/папки (начинающиеся с .)
    if ignore_hidden and name.startswith('.'):
        return True

    # Проверка по паттернам
    for pattern in ignore_patterns:
        if pattern in name:
            return True
        if pattern in path_str:
            return True

    return False


def get_folder_structure(root_path, ignore_patterns=None, max_items=25, ignore_hidden=True):
    """
    Рекурсивно собирает структуру файлов и папок начиная с root_path
    """
    if ignore_patterns is None:
        ignore_patterns = {
            '__pycache__', '.git', '.vscode', '.idea', 'node_modules',
            '.DS_Store', 'Thumbs.db', '.pytest_cache', '.mypy_cache',
            'build', 'dist', '*.egg-info', 'venv', 'env', '.env',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll',
            '*.log', 'tmp', 'temp', 'cache'
        }

    structure = {}
    root_path = Path(root_path)

    try:
        entries = list(root_path.iterdir())
    except PermissionError:
        return structure

    # Сортируем и фильтруем записи
    filtered_entries = []
    for entry in entries:
        if not should_ignore(entry, ignore_patterns, ignore_hidden):
            filtered_entries.append(entry)

    # Сортируем: сначала папки, потом файлы
    filtered_entries.sort(key=lambda x: (x.is_file(), x.name.lower()))

    for entry in filtered_entries[:max_items]:  # Ограничиваем обработку
        if entry.is_file():
            if root_path not in structure:
                structure[root_path] = []
            structure[root_path].append(entry.name)
        elif entry.is_dir():
            # Рекурсивно обрабатываем подпапку
            substructure = get_folder_structure(entry, ignore_patterns, max_items, ignore_hidden)
            structure.update(substructure)

            if root_path not in structure:
                structure[root_path] = []
            structure[root_path].append(entry.name)

    # Добавляем информацию о пропущенных элементах
    if len(filtered_entries) > max_items:
        if root_path not in structure:
            structure[root_path] = []
        structure[root_path].append(f"... (пропущено {len(filtered_entries) - max_items} элементов)")

    return structure


def print_folder_structure(root_path, ignore_patterns=None, max_display_items=25):
    """
    Выводит структуру папок и файлов
    """
    try:
        structure = get_folder_structure(root_path, ignore_patterns, max_display_items)

        # Сортируем папки для consistent вывода
        sorted_folders = sorted(structure.keys())

        for folder in sorted_folders:
            # Получаем относительный путь для красивого отображения
            relative_path = folder.relative_to(root_path)
            display_name = str(relative_path) if str(relative_path) != '.' else os.path.basename(root_path)

            contents = structure[folder]

            # Форматируем вывод
            if contents:
                print(f"{display_name}/: {contents}")
            else:
                print(f"{display_name}/: [пустая папка]")

    except Exception as e:
        print(f"Ошибка: {e}")


def get_custom_ignore_patterns():
    """
    Запрашивает у пользователя дополнительные паттерны для игнорирования
    """
    custom_patterns = set()
    print("\nХотите добавить свои паттерны для игнорирования? (y/n): ", end='')
    response = input().strip().lower()

    if response in ['y', 'yes', 'д', 'да']:
        print("Введите паттерны через запятую (например: *.tmp, backup, test*): ")
        user_input = input().strip()
        if user_input:
            patterns = [p.strip() for p in user_input.split(',')]
            custom_patterns.update(patterns)

    return custom_patterns


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python folder_structure.py <путь_к_папке>")
        sys.exit(1)

    folder_path = sys.argv[1]

    if not os.path.exists(folder_path):
        print(f"Ошибка: путь '{folder_path}' не существует")
        sys.exit(1)

    if not os.path.isdir(folder_path):
        print(f"Ошибка: '{folder_path}' не является папкой")
        sys.exit(1)

    # Базовые паттерны для игнорирования
    ignore_patterns = {
        '__pycache__', '.git', '.vscode', '.idea', 'node_modules',
        '.DS_Store', 'Thumbs.db', '.pytest_cache', '.mypy_cache',
        'build', 'dist', '*.egg-info', 'venv', 'env', '.env',
        '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll',
        '*.log', 'tmp', 'temp', 'cache', '*.class',
        '*.jar', '*.war', '*.ear', '*.zip', '*.tar.gz'
    }

    # Запрашиваем пользовательские паттерны
    custom_patterns = get_custom_ignore_patterns()
    ignore_patterns.update(custom_patterns)

    print(f"Структура папки: {folder_path}")
    print(f"Игнорируемые паттерны: {sorted(ignore_patterns)}")
    print("-" * 50)

    print_folder_structure(folder_path, ignore_patterns)