import os

from rich.syntax import Syntax
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, ListView, ListItem, Label

from codelimit.common.report.ReportReader import ReportReader
from codelimit.common.report.ReportUnit import format_report_unit
from codelimit.common.source_utils import get_location_range
from codelimit.common.tui.CodeScreen import CodeScreen


class CodeLimitApp(App):
    BINDINGS = [('q', 'quit', 'Quit')]

    def __init__(self):
        super().__init__()
        self.report = None
        self.code_screen = CodeScreen()

    def compose(self) -> ComposeResult:
        with open('codelimit.json', 'r') as file:
            json = file.read()
        report = ReportReader.from_json(json)
        self.report = report
        yield Header()
        yield Footer()
        list_view = ListView()
        for idx, unit in enumerate(self.report.all_report_units_sorted_by_length_asc()):
            list_view.append(ListItem(Label(format_report_unit(unit)), name=f'{idx}'))
        yield list_view
        self.set_focus(list_view)
        self.install_screen(self.code_screen, 'code_screen')

    def on_list_view_selected(self, event: ListView.Selected):
        idx = int(event.item.name)
        unit = self.report.all_report_units_sorted_by_length_asc()[idx]
        file_path = os.path.join('.', unit.file)
        with open(file_path) as file:
            code = file.read()
        snippet = get_location_range(code, unit.measurement.start, unit.measurement.end)
        rich_snippet = Syntax(snippet, 'python', line_numbers=True)
        self.code_screen.set_code(rich_snippet)
        self.push_screen('code_screen')

    def action_quit(self) -> None:
        self.exit()
