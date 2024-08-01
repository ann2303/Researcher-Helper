# Researcher-Helper
Инструмент, формирующий таблицу со статьями и их краткими содержаниями по заданной исследователем теме.
Цель: получить примерное представление об области исследования. 



# Install

```
pipenv shell
pipenv install
```


# Usage


python3 src/main.py [-h] [--save_directory SAVE_DIRECTORY] [--query QUERY] [--database {semantic_scholar,arxiv}] [--config CONFIG]


## Arguments

- `-h`, `--help`: Show this help message and exit
- `--save_directory SAVE_DIRECTORY`: Path to the directory where the results will be saved
- `--query QUERY`: The research topic to search for
- `--database {semantic_scholar,arxiv}`: The database to use for the search (either 'semantic_scholar' or 'arxiv')
- `--config CONFIG`: Path to the configuration file

## Example


python3 src/main.py --save_directory ./results --query "machine learning" --database arxiv --config ./config.json


This command will search for articles about "machine learning" in the arXiv database, using the configuration specified in `config.json`, and save the results in the `./results` directory.


## Output Example

In result_example.html