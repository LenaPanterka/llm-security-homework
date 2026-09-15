# LLM Security Homework

Учебный проект для сравнения уязвимой и защищённой версий LLM-агента.

## Проект демонстрирует:

работу LLM-агента с SQL tool;
работу с внутренними документами;
различия между уязвимой и защищённой версиями;
автоматизированный прогон тестов;
сохранение результатов в JSON-отчёт.

## Структура проекта

app/
database.py
rag.py
vulnerable_agent.py
protected_agent.py

data/
app.db
docs/

tests/
payloads.json
run_tests.py
results.json

Dockerfile
docker-compose.yml
REPORT.md
requirements.txt

## Требования

### Для запуска нужны:

Docker Desktop
Python 3
Ollama
модель llama3.2:latest

### Установка модели

Проверить доступные модели:

ollama list

Если llama3.2:latest отсутствует:

ollama pull llama3.2

### Запуск проекта

Обе версии агента запускаются одной командой:

docker compose up --build

После запуска:

vulnerable agent: http://localhost:8000
protected agent: http://localhost:8001
Health check

Уязвимая версия:

http://localhost:8000/health

Защищённая версия:

http://localhost:8001/health

Ожидаемый результат:

{
"status": "ok"
}

API

Основной endpoint:

POST /chat

Пример тела запроса:

{
"message": "Покажи список заказов."
}

### Автоматизированный тестовый прогон

Установить Python-зависимости:

python -m pip install -r requirements.txt

Запустить тесты:

python tests/run_tests.py

Набор тестовых входов находится в:

tests/payloads.json

Результат прогона сохраняется в:

tests/results.json

Security Report

Описание найденных проблем, поведения уязвимой версии и защитных механизмов находится в:

REPORT.md

В отчёте задокументированы 6 классов security-проблем и результаты сравнения vulnerable/protected версий.
