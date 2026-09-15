import argparse

import ollama


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Генерация тестовых сценариев с помощью Ollama."
    )

    parser.add_argument(
        "count",
        type=int,
        help="Количество тестовых сценариев для генерации.",
    )

    return parser.parse_args()


def validate_count(count: int) -> None:
    if count < 2:
        raise ValueError(
            "Количество сценариев должно быть не меньше 2, "
            "чтобы включить позитивные и негативные проверки."
        )


def build_prompt(count: int) -> str:
    return f"""
Ты — опытный QA-инженер.

Создай ровно {count} тестовых сценариев для формы регистрации пользователя.

Форма содержит:
- поле имени пользователя;
- поле пароля;
- поле подтверждения пароля;
- кнопку «Зарегистрировать».

Требования:
1. Сценарии должны включать позитивные и негативные проверки.
2. Если запрошено два или более сценариев, должен быть минимум один позитивный
   и минимум один негативный сценарий.
3. Создай ровно {count} сценариев.
4. Пронумеруй их последовательно: TC-01, TC-02, TC-03 и далее.
5. Не повторяй одинаковые проверки.
6. Используй грамотный и естественный русский язык.
7. Не смешивай русский и английский языки внутри слов и предложений.
8. Заголовок каждого сценария должен быть коротким и понятным.
9. Верни результат только в формате Markdown.
10. Не добавляй вступление, заключение или пояснения вне сценариев.
11. Перед отправкой проверь орфографию, нумерацию и Markdown-разметку.

Примеры корректных заголовков:
- ## TC-01: Успешная регистрация с корректными данными
- ## TC-02: Регистрация с несовпадающими паролями
- ## TC-03: Попытка регистрации без имени пользователя

Используй для каждого сценария следующую структуру:

## TC-XX: Название сценария

**Тип:** Позитивный или Негативный

**Предусловия:**
- предусловие или «Отсутствуют»

**Тестовые данные:**
- Имя пользователя: значение
- Пароль: значение
- Подтверждение пароля: значение

**Шаги:**
1. Первый шаг
2. Второй шаг
3. Последующие шаги

**Ожидаемый результат:**
Описание ожидаемого поведения системы.
""".strip()


def generate_scenarios(count: int) -> str:
    prompt = build_prompt(count)

    try:
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты — профессиональный русскоязычный QA-инженер. "
                        "Пиши грамотно и ясно. "
                        "Перед отправкой ответа проверь заголовки "
                        "и нумерацию тестовых сценариев."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            options={
                "temperature": 0.2,
            },
        )
    except Exception as error:
        raise RuntimeError(
            "Не удалось получить ответ от Ollama. "
            "Проверьте, что Ollama запущена и модель "
            "'llama3.2:latest' установлена."
        ) from error

    scenarios = response["message"]["content"].strip()

    if not scenarios:
        raise RuntimeError("Модель вернула пустой ответ.")

    return scenarios


def save_scenarios(scenarios: str, filename: str) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(scenarios)
    except OSError as error:
        raise RuntimeError(
            f"Не удалось сохранить сценарии в файл '{filename}'."
        ) from error


def main() -> None:
    arguments = parse_arguments()

    try:
        validate_count(arguments.count)

        print("Генерация тестовых сценариев...")

        scenarios = generate_scenarios(arguments.count)

        output_filename = "generated_scenarios.md"

        save_scenarios(scenarios, output_filename)

    except (ValueError, RuntimeError) as error:
        print(f"Ошибка: {error}")
        return

    print()
    print(scenarios)
    print()
    print(f"Сценарии сохранены в файл: {output_filename}")


if __name__ == "__main__":
    main()