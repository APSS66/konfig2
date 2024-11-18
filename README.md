# Git dependency visualizer

## Описание задания

Разработать инструмент командной строки для визуализации графа зависимостей, включая транзитивные зависимости. Сторонние программы или библиотеки для получения зависимостей использовать нельзя. Зависимости определяются для git-репозитория. Для описания графа зависимостей используется представление Graphviz. Визуализатор должен выводить результат на экран в виде графического изображения графа. Построить граф зависимостей для коммитов, в узлах которого содержатся номера коммитов в хронологическом порядке. Граф необходимо строить только для коммитов позже заданной даты.

## Настройки
Настройки задаются ключами командной строки :
• Путь к программе для визуализации графов.
• Путь к анализируемому репозиторию.
• Дата коммитов в репозитории.
### Сборка и запуск

Для сборки и запуска проекта в вашей системе должен быть установлен Python. Выполните следующие действия:

1. **Клонирование репозитория**: 
    ```bash
    git clone <repository-url>
    ```

2. **Перемещение в директорию проекта**:
    ```bash
    cd <project-directory>
    ```
    
3. **Запуск эмулятора с переданными параметрами**:
    ```bash
    python git_dependency_visualizer.py <path-to-visualizer> <path-to-local-git-repository> <date>```


## Примеры использования
Пример запуска со следующими параметрами: /bin/xdot /home/S66/konfig1/.git 2024-11-10
![пример запуска программы со следующими параметрами](/images/result-screen)
Пример сформированного dot-файла с graphviz-представлением
![пример dot-файла](/images/dot)
## Результаты тестов
![Результаты прогона тестов](/images/tests-screen)
Все функции эмулятора были протестированы. Результаты тестов представлены на скриншоте выше
