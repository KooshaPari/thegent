"""Sortable/paginated table widget for compositor sidebars (WL-017)."""

from __future__ import annotations

from textual.widget import Widget
from textual.widgets import DataTable


class TableWidget(Widget):
    """Data table with in-memory sort and simple pagination."""

    DEFAULT_CSS = """
    TableWidget {
        width: 1fr;
        height: 1fr;
        border: solid $secondary;
    }
    """

    def __init__(self, page_size: int = 20) -> None:
        super().__init__()
        self._page_size = max(1, page_size)
        self._columns: list[str] = []
        self._rows: list[tuple[str, ...]] = []
        self._page = 0

    def compose(self):
        yield DataTable(id="table-widget-grid", zebra_stripes=True)

    def _grid(self) -> DataTable:
        return self.query_one("#table-widget-grid", DataTable)

    def set_columns(self, columns: list[str]) -> None:
        self._columns = list(columns)
        if self.is_attached:
            grid = self._grid()
            grid.clear(columns=True)
            for col in self._columns:
                grid.add_column(col)
            self._render_page()

    def set_rows(self, rows: list[tuple[str, ...]]) -> None:
        self._rows = [tuple(str(c) for c in row) for row in rows]
        self._page = 0
        if self.is_attached:
            self._render_page()

    def sort_by(self, column_index: int, reverse: bool = False) -> None:
        if not self._rows:
            return
        if column_index < 0 or column_index >= len(self._rows[0]):
            return
        self._rows.sort(key=lambda r: r[column_index], reverse=reverse)
        if self.is_attached:
            self._render_page()

    def next_page(self) -> None:
        max_page = max(0, (len(self._rows) - 1) // self._page_size)
        self._page = min(max_page, self._page + 1)
        if self.is_attached:
            self._render_page()

    def prev_page(self) -> None:
        self._page = max(0, self._page - 1)
        if self.is_attached:
            self._render_page()

    def _render_page(self) -> None:
        grid = self._grid()
        if not self._columns:
            grid.clear(columns=True)
            return
        grid.clear(columns=True)
        for col in self._columns:
            grid.add_column(col)

        start = self._page * self._page_size
        end = start + self._page_size
        for row in self._rows[start:end]:
            grid.add_row(*row)
