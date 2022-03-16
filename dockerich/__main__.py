"""

Demonstrates a dynamic Layout

"""

from datetime import datetime, timedelta
import docker

from time import sleep
from rich.columns import Columns
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
import pandas as pd
"""
This example shows how to display content in columns.

The data is pulled from https://randomuser.me
"""

from rich.spinner import Spinner

from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table

"""Lite simulation of the top linux command."""
import random
import sys
import time
from dataclasses import dataclass

from rich import box
from rich.console import Console
from rich.live import Live
from rich.table import Table

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


@dataclass
class Process:
    pid: int
    command: str
    cpu_percent: float
    memory: int
    start_time: datetime
    thread_count: int
    state: Literal["running", "sleeping"]

    @property
    def memory_str(self) -> str:
        if self.memory > 1e6:
            return f"{int(self.memory/1e6)}M"
        if self.memory > 1e3:
            return f"{int(self.memory/1e3)}K"
        return str(self.memory)

    @property
    def time_str(self) -> str:
        return str(datetime.now() - self.start_time)


def generate_process(pid: int) -> Process:
    return Process(
        pid=pid,
        command=f"Process {pid}",
        cpu_percent=random.random() * 20,
        memory=random.randint(10, 200) ** 3,
        start_time=datetime.now()
        - timedelta(seconds=random.randint(0, 500) ** 2),
        thread_count=random.randint(1, 32),
        state="running" if random.randint(0, 10) < 8 else "sleeping",
    )


def create_process_table(height: int) -> Table:

    processes = sorted(
        [generate_process(pid) for pid in range(height)],
        key=lambda p: p.cpu_percent,
        reverse=True,
    )
    table = Table(
        "PID", "Command", "CPU %", "Memory", "Time", "Thread #", "State", box=box.SIMPLE
    )

    for process in processes:
        table.add_row(
            str(process.pid),
            process.command,
            f"{process.cpu_percent:.1f}",
            process.memory_str,
            process.time_str,
            str(process.thread_count),
            process.state,
        )

    return table

def calculate_cpu_percent(d):
    cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
    cpu_percent = 0.0
    cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                float(d["precpu_stats"]["cpu_usage"]["total_usage"])
    system_delta = d["cpu_stats"]["cpu_usage"]["total_usage"]
    if system_delta > 0.0:
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    return '{0:.2f}'.format(cpu_percent)

def calculate_memory_percent(d):
    return '{0:.2f}'.format(d["memory_stats"]["max_usage"]/d["memory_stats"]["limit"])
    
def get_name(c):
    return c.attrs["Name"][1:]


class DockerColumns:
    """Renders the time in the center of the screen."""
    def __init__(self, client, is_dev=None) -> None:
        self._client = client
        self._is_dev = is_dev
        self._stats = {}
        
    def __rich__(self) -> Columns:
        containers = self._client.containers.list()
        for c in containers:
            name = get_name(c)
            if not name in self._stats:
                self._stats[name] = c.stats(stream=True, decode=True)
                
        containers =  dict([(get_name(c), {"info":c, "stat":self._stats[get_name(c)]}) for c in containers])
        if self._is_dev is not None:
            if self._is_dev:
                containers =  dict([(k, v) for k, v in containers.items() if k.startswith("dev_")])
            else:
                containers =  dict([(k, v) for k, v in containers.items() if not k.startswith("dev_")])
    
        panels = []
        for name, container in containers.items():
            for s in container["stat"]:
                panels.append(Panel(
                    Spinner("circle", text=self.make_panel(container, s)),
                    title=f"[b]{name}[/b]",
                    expand=True))
                break
        return Columns(panels)
    
    
    @staticmethod
    def make_panel(container, stat):
        state = container["info"].attrs["State"]["Status"]
        cpu = calculate_cpu_percent(stat)
        mem = calculate_memory_percent(stat)
        color_state = "yellow" if not state=="running" else "green"
        cpu_color = "blue" if int(eval(cpu))<70 else "yellow"
        mem_color = "blue" if int(eval(mem))<70 else "yellow"
        return f"[{color_state}]{state}\n[{cpu_color}]CPU [{cpu}]\n[{mem_color}]MEM [{mem}]"




class DockerTable:
    """Renders the time in the center of the screen."""
    def __init__(self, client, full=False) -> None:
        self._client = client
        self._full = full
        
    def __rich__(self) -> Table:
        containers = client.containers.list()
        if self._full:
            stats = [c.stats(stream=True, decode=True) for c in containers]
        else:
            stats = [None for c in containers]

        records = []
        for c, stat in zip(containers, stats):
            d = {
                "name": get_name(c),
                "image": c.attrs["Config"]["Image"],
                "Ports": "",
            }
            try:
                ports=[]
                for k, v in c.ports.items():
                    if v is not None:
                        ports.append(f"{k}:{v[0]['HostPort']}")
                    else:
                        ports.append(f"{k}")
                d["Ports"]= "\n".join(ports)
            except:
                pass
            try:
                for s in stat:
                    d["CPU %"] = calculate_cpu_percent(s)
                    d["MEM %"] = calculate_memory_percent(s)
                    break
            except TypeError:
                pass
            
            records.append(d)

        df = pd.DataFrame.from_records(records)
        table = Table(title="Containers", expand=True, box=box.HORIZONTALS, show_lines=True)
        for column in df.columns:
            table.add_column(str(column))
                
        for index, value_list in enumerate(df.values.tolist()):
            row = [str(x) for x in value_list]
            table.add_row(*row)
                
        return table

console = Console()
layout = Layout()

layout.split(
    Layout(name="header",   size=1),
    Layout(name="main",     ratio=1),
    # Layout(name="footer",   size=10),
)

layout["main"].split_row(
    Layout(name="side"),
    Layout(name="body", ratio=2)
    )

layout["side"].split(
    # Layout(), 
    Layout(name="dev_containers"),
    Layout(name="containers"),
)

layout["body"].update(
    Align.center(
        Text(
            """This is a demonstration of rich.Layout\n\nHit Ctrl+C to exit""",
            justify="center",
        ),
        vertical="middle",
    )
)


class Clock:
    """Renders the time in the center of the screen."""

    def __rich__(self) -> Text:
        return Text(datetime.now().ctime(), style="bold magenta", justify="center")
client = docker.from_env()

containers = client.containers.list()

layout["header"].update(Clock())
layout["body"].update(DockerTable(client, full=False))
layout["dev_containers"].update(DockerColumns(client, is_dev=True))
layout["containers"].update(DockerColumns(client, is_dev=False))
# layout["body"].update(create_process_table(console.size.height - 4))

with Live(layout, screen=True, redirect_stderr=False) as live:
    try:
        while True:
            # live.update(create_process_table(console.size.height - 4), refresh=True)
            sleep(0.1)
    except KeyboardInterrupt:
        pass
