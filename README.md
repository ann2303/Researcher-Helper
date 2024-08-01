# Researcher-Helper
Инструмент, формирующий таблицу со статьями и их краткими содержаниями по заданной исследователем теме.
Цель: получить примерное представление об области исследования. 

Структура таблицы:
|Статья|Автор|Год|Ссылка|Краткое описание|
|------|-----|---|------|----------------|


# Install

```
pipenv shell
pipenv install
```

# Run

```
python3 src/main.py --save_directory <path_to_save_directory> --query <topic_name> --database [semantic_scholar|arxiv] --config <path_to_config>
```

