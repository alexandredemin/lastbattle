# Путь к исходникам и билд-директории
SRC_DIR=src
BUILD_DIR=$(SRC_DIR)/build/web
PORT=8000

.PHONY: build serve run clean

# Сборка проекта (запускает pygbag для сборки, без сервера)
build:
	python -m pygbag $(SRC_DIR)

# Запуск простого HTTP-сервера для уже собранной версии
serve:
	python -m http.server --directory $(BUILD_DIR) $(PORT) --bind 0.0.0.0

# Запуск сборки, затем запуск сервера (в одном терминале)
run: build serve

# Очистка билд-директории (если нужно)
clean:
	rm -rf $(BUILD_DIR)