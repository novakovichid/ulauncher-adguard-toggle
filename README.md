# ulauncher-adguard-toggle

Простое расширение Ulauncher для управления AdGuard VPN:
- показывает текущий статус (`adguardvpn status`) сразу после ввода ключевого слова;
- выполняет `adguardvpn connect`;
- выполняет `adguardvpn disconnect`;
- сразу обновляет статус после действия.

## Установка

1. Откройте Ulauncher → `Extensions` → `Add extension`.
2. Вставьте URL этого репозитория (или локальный путь).
3. По умолчанию ключевое слово: `agv`.

## Настройки

- `CLI command` — путь к бинарнику AdGuard VPN CLI (по умолчанию `adguardvpn`).

## Использование

1. Введите `agv` в Ulauncher.
2. Первая строка покажет текущий статус VPN.
3. Выберите `Подключить AdGuard VPN` или `Отключить AdGuard VPN`.
4. После выполнения команда статус будет перечитан автоматически.
