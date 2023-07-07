import json
import urllib
import urllib.request
import webbrowser
from dataclasses import dataclass

from pgcli.pyev import Visualizer

API_URL = "https://explain.dalibo.com/new.json"


@dataclass
class PevResponse:
    id: str
    delete_key: str

    @property
    def url(self) -> str:
        return f"https://explain.dalibo.com/plan/{self.id}"

    @property
    def delete_url(self) -> str:
        return f"{self.url}/{self.delete_key}"

    def delete(self) -> None:
        """Deletes the plan from explain.dalibo"""
        urllib.request.urlopen(urllib.request.Request(self.delete_url))

    def __repr__(self) -> str:
        return f"PevResult(url={self.url})"


"""Explain response output adapter"""


def upload_sql_plan(query: str, plan: str, title: str) -> PevResponse:
    """Uploads a sql plan to explain.dalibo for visualization"""
    payload = json.dumps(
        {"title": title, "plan": json.dumps(plan), "query": query}
    ).encode()
    with urllib.request.urlopen(
        urllib.request.Request(
            API_URL,
            headers={
                "Content-Type": "application/json",
            },
            data=payload,
        )
    ) as response:
        data = json.loads(response.read())
        return PevResponse(id=data["id"], delete_key=data["deleteKey"])


class ExplainOutputFormatter:
    def __init__(self, max_width=None, title=None, sql_text=None, **kwargs):
        self.sql_text = sql_text
        self.title = title
        self.max_width = max_width or 100

    def format_output(self, cur, headers, **output_kwargs):
        # explain query results should always contain 1 row each
        [(data,)] = list(cur)
        explain_list = json.loads(data)
        visualizer = Visualizer(self.max_width)
        for explain in explain_list:
            pev = upload_sql_plan(self.sql_text, plan=explain, title=self.title)
            webbrowser.open_new_tab(pev.url)
            visualizer.load(explain)
            yield f"PEV Visualiztion {pev.url}\n{visualizer.get_list()}"
