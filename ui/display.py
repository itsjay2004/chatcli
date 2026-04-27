from __future__ import annotations

from typing import Iterable

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table


class ChatDisplay:
    def __init__(self) -> None:
        self.console = Console()

    def banner(self) -> None:
        self.console.print(
            Panel.fit(
                "[bold cyan]ChatCLI[/bold cyan] [dim]Modern Terminal AI Chat[/dim]\\n"
                "Type [bold]/help[/bold] to view commands.",
                border_style="bright_blue",
            )
        )

    def show_user_message(self, content: str) -> None:
        self.console.print(
            Panel(
                Markdown(content),
                title="🧑 You",
                title_align="left",
                border_style="green",
                padding=(0, 1),
            )
        )

    def show_assistant_message(self, content: str, model_name: str | None = None) -> None:
        title = "🤖 Assistant" if not model_name else f"🤖 Assistant · {model_name}"
        self.console.print(
            Panel(
                Markdown(content, code_theme="monokai"),
                title=title,
                title_align="left",
                border_style="cyan",
                padding=(0, 1),
            )
        )

    def show_system(self, message: str, style: str = "bold yellow") -> None:
        self.console.print(message, style=style)

    def show_error(self, message: str) -> None:
        self.console.print(Panel(message, title="Error", border_style="red", style="bold red"))

    def show_history(self, rows: Iterable[tuple[int, str, str]]) -> None:
        table = Table(title="Saved Chats", header_style="bold magenta")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Title", style="white")
        table.add_column("Saved At", style="green")

        count = 0
        for row_id, title, created_at in rows:
            count += 1
            table.add_row(str(row_id), title, created_at)

        if count == 0:
            self.show_system("No saved chats found.", style="yellow")
            return

        self.console.print(table)

    def clear_screen(self) -> None:
        self.console.clear()

    def print_help(self) -> None:
        table = Table(title="Commands", header_style="bold blue")
        table.add_column("Command", style="cyan")
        table.add_column("Description", style="white")
        table.add_row("/help", "Show command list")
        table.add_row("/clear", "Clear visible screen (keeps session messages)")
        table.add_row("/exit", "Save and exit safely")
        table.add_row("/save", "Save current chat now")
        table.add_row("/history", "List last 10 saved chats")
        table.add_row("/load <id>", "Load chat from /history index")
        table.add_row("/delete <id>", "Delete a saved chat")
        table.add_row("/config", "Open interactive configuration")
        self.console.print(table)
