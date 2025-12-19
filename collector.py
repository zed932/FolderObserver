import os
import argparse


def collect_python_code(root_dir, output_file="all_code.txt", exclude_dirs=None):
    """
    Собирает весь Python код из директории и поддиректорий в один файл

    Args:
        root_dir (str): Корневая директория для поиска
        output_file (str): Имя выходного файла
        exclude_dirs (list): Список директорий для исключения
    """

    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', '.git', 'venv', 'env', 'node_modules']

    python_files = []

    # Рекурсивно находим все .py файлы
    for root, dirs, files in os.walk(root_dir):
        # Исключаем ненужные директории
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                python_files.append(full_path)

    # Сортируем файлы для удобства
    python_files.sort()

    # Записываем код в выходной файл
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for file_path in python_files:
            # Получаем относительный путь для названия
            relative_path = os.path.relpath(file_path, root_dir)

            # Записываем название файла
            outfile.write(f"# {relative_path}\n")

            try:
                # Читаем и записываем содержимое файла
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()
                    outfile.write(content)

                # Добавляем разделитель между файлами
                outfile.write("\n\n" + "=" * 80 + "\n\n")

                print(f"Обработан: {relative_path}")

            except Exception as e:
                print(f"Ошибка при чтении файла {file_path}: {e}")
                outfile.write(f"# Ошибка при чтении файла: {e}\n\n")

    print(f"\nГотово! Собрано {len(python_files)} файлов.")
    print(f"Результат сохранен в: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Сборщик Python кода из директории')
    parser.add_argument('directory', nargs='?', default='.',
                        help='Корневая директория для поиска (по умолчанию: текущая директория)')
    parser.add_argument('-o', '--output', default='all_code.txt',
                        help='Имя выходного файла (по умолчанию: all_code.txt)')
    parser.add_argument('-e', '--exclude', nargs='+',
                        default=['__pycache__', '.git', 'venv', 'env', 'node_modules'],
                        help='Директории для исключения')

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        print(f"Ошибка: Директория '{args.directory}' не существует!")
        return

    collect_python_code(args.directory, args.output, args.exclude)


if __name__ == "__main__":
    main()