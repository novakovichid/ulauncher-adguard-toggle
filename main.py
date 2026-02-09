import subprocess

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

ICON_PATH = "images/icon.png"


class AdGuardVpnExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        return RenderResultListAction(build_items(extension))


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        action = event.get_data().get("action")
        if action in {"connect", "disconnect"}:
            run_cli(extension, action)
        return RenderResultListAction(build_items(extension))


def get_cli_command(extension):
    cli = extension.preferences.get("adguard_cli", "adguardvpn").strip()
    return cli or "adguardvpn"


def run_cli(extension, subcommand):
    cli = get_cli_command(extension)
    try:
        subprocess.run(
            [cli, subcommand],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return


def read_status(extension):
    cli = get_cli_command(extension)
    try:
        result = subprocess.run(
            [cli, "status"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
            check=False,
        )
    except OSError:
        return {
            "label": "CLI не найден",
            "description": f"Не удалось запустить '{cli}'. Проверьте путь в настройках.",
            "connected": False,
        }
    except subprocess.SubprocessError:
        return {
            "label": "Ошибка чтения статуса",
            "description": "Не удалось получить статус AdGuard VPN.",
            "connected": False,
        }

    output = (result.stdout or result.stderr or "").strip()
    normalized = output.lower()

    connected = "connected" in normalized and "disconnected" not in normalized
    disconnected = "disconnected" in normalized or "not connected" in normalized

    if connected:
        label = "VPN: подключен"
    elif disconnected:
        label = "VPN: отключен"
    else:
        label = "VPN: статус не распознан"

    if not output:
        output = "Команда не вернула вывод."

    return {
        "label": label,
        "description": output,
        "connected": connected,
    }


def build_items(extension):
    status = read_status(extension)
    if status["connected"]:
        toggle_action = "disconnect"
        toggle_label = "Toggle: отключить AdGuard VPN"
        secondary_action = "connect"
        secondary_label = "Подключить AdGuard VPN"
    else:
        toggle_action = "connect"
        toggle_label = "Toggle: подключить AdGuard VPN"
        secondary_action = "disconnect"
        secondary_label = "Отключить AdGuard VPN"

    items = [
        ExtensionResultItem(
            icon=ICON_PATH,
            name=toggle_label,
            description=f"{status['label']}. Нажмите, чтобы переключить.",
            on_enter=ExtensionCustomAction({"action": toggle_action}, keep_app_open=True),
        )
    ]

    items.append(
        ExtensionResultItem(
            icon=ICON_PATH,
            name=status["label"],
            description=status["description"],
            on_enter=ExtensionCustomAction({"action": "refresh"}, keep_app_open=True),
        )
    )

    items.append(
        ExtensionResultItem(
            icon=ICON_PATH,
            name=secondary_label,
            description="Альтернативное действие",
            on_enter=ExtensionCustomAction({"action": secondary_action}, keep_app_open=True),
        )
    )

    items.append(
        ExtensionResultItem(
            icon=ICON_PATH,
            name="Обновить статус",
            description="Повторно выполнить 'adguardvpn status'",
            on_enter=ExtensionCustomAction({"action": "refresh"}, keep_app_open=True),
        )
    )

    return items


if __name__ == "__main__":
    AdGuardVpnExtension().run()
