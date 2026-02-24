from __future__ import annotations

from typing import Any, ClassVar

from thegent.infra.fast_yaml_parser import yaml_load, yaml_dump
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, ListItem, ListView, Select

from thegent.config import get_settings


class ModelRouteItem(ListItem):
    """ListItem subclass carrying model_id and route_index metadata."""

    def __init__(self, *children: Any, model_id: str, route_index: int) -> None:
        super().__init__(*children)
        self.model_id: str = model_id
        self.route_index: int = route_index


class ModelAddModal(ModalScreen[dict[str, Any]]):
    """Modal for adding a new model route."""

    def compose(self) -> ComposeResult:
        yield Vertical(
            Label("Add New Model Route", id="title"),
            Label("Canonical Model ID (e.g. gpt-4o):"),
            Input(placeholder="gpt-4o", id="model_id"),
            Label("Provider (e.g. openai, anthropic, custom):"),
            Input(placeholder="openai", id="provider"),
            Label("Model Alias/Name for Provider:"),
            Input(placeholder="gpt-4o-2024-05-13", id="model_alias"),
            Label("Backend Type:"),
            Select([("direct", "direct"), ("proxy", "proxy")], value="direct", id="backend_type"),
            Label("Priority (lower = higher priority):"),
            Input(placeholder="0", id="priority"),
            Label("Cost Weight (0.1 = cheap, 1.0 = normal):"),
            Input(placeholder="1.0", id="cost_weight"),
            Horizontal(
                Button("Cancel", variant="error", id="cancel"),
                Button("Save", variant="success", id="save"),
                classes="buttons",
            ),
            id="modal_container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
        elif event.button.id == "save":
            model_id = self.query_one("#model_id", Input).value
            provider = self.query_one("#provider", Input).value
            model_alias = self.query_one("#model_alias", Input).value
            backend_type = self.query_one("#backend_type", Select).value
            priority_val = self.query_one("#priority", Input).value
            cost_val = self.query_one("#cost_weight", Input).value

            try:
                priority = int(priority_val or "0")
            except ValueError:
                priority = 0

            try:
                cost_weight = float(cost_val or "1.0")
            except ValueError:
                cost_weight = 1.0

            if model_id and provider and model_alias:
                self.dismiss(
                    {
                        "model_id": model_id,
                        "route": {
                            "provider": provider,
                            "model_alias": model_alias,
                            "backend_type": backend_type,
                            "priority": priority,
                            "cost_weight": cost_weight,
                        },
                    }
                )


class ModelsTUI(App):
    """TUI for managing custom models."""

    TITLE = "thegent Model Manager"

    CSS = """
    #main_container {
        padding: 1;
    }
    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        background: $accent;
        color: white;
        margin-bottom: 1;
    }
    ListView {
        border: solid $accent;
        height: 1fr;
        margin-bottom: 1;
    }
    .buttons {
        height: auto;
        align: center middle;
    }
    Button {
        margin: 0 1;
    }
    #modal_container {
        width: 60;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1;
    }
    #modal_container Label {
        margin-top: 1;
    }
    #modal_container #title {
        background: $accent;
        color: white;
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    """

    BINDINGS: ClassVar[list[Any]] = [
        Binding("q", "quit", "Quit"),
        Binding("a", "add_model", "Add Model"),
        Binding("d", "delete_model", "Delete Selected"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.settings = get_settings()
        self.custom_path = self.settings.custom_models_path
        self.custom_data: dict[str, list[dict]] = {}
        self.load_data()

    def load_data(self) -> None:
        if self.custom_path.exists():
            try:
                self.custom_data = yaml.safe_load(self.custom_path.read_text(encoding="utf-8")) or {}
            except Exception:
                self.custom_data = {}
        else:
            self.custom_data = {}

    def save_data(self) -> None:
        self.custom_path.parent.mkdir(parents=True, exist_ok=True)
        self.custom_path.write_text(yaml.dump(self.custom_data), encoding="utf-8")

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Label("Custom Models Catalog", id="title"),
            ListView(id="models_list"),
            Horizontal(
                Button("Add Model (a)", variant="primary", id="add_btn"),
                Button("Delete Selected (d)", variant="error", id="del_btn"),
                classes="buttons",
            ),
            id="main_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_list()

    def refresh_list(self) -> None:
        list_view = self.query_one("#models_list", ListView)
        list_view.clear()

        for model_id, routes in self.custom_data.items():
            for i, r in enumerate(routes):
                label = f"{model_id} via {r['provider']} ({r['model_alias']}) - {r['backend_type']} - Prio: {r['priority']} - Cost: {r['cost_weight']}"
                item = ModelRouteItem(Label(label), model_id=model_id, route_index=i)
                list_view.append(item)

    def action_add_model(self) -> None:
        def handle_add(result: dict[str, Any] | None) -> None:
            if result:
                mid = result["model_id"]
                if mid not in self.custom_data:
                    self.custom_data[mid] = []
                self.custom_data[mid].append(result["route"])
                self.save_data()
                self.refresh_list()

        self.push_screen(ModelAddModal(), handle_add)

    def action_delete_model(self) -> None:
        list_view = self.query_one("#models_list", ListView)
        if list_view.index is not None:
            item = list_view.children[list_view.index]
            mid = getattr(item, "model_id", None)
            idx = getattr(item, "route_index", None)
            if mid is not None and idx is not None:
                self.custom_data[mid].pop(idx)
                if not self.custom_data[mid]:
                    del self.custom_data[mid]
                self.save_data()
                self.refresh_list()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add_btn":
            self.action_add_model()
        elif event.button.id == "del_btn":
            self.action_delete_model()


def models_tui_main():
    ModelsTUI().run()


if __name__ == "__main__":
    models_tui_main()
