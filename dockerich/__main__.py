"""

Demonstrates a dynamic Layout

"""

from datetime import datetime, timedelta, timezone
import docker

from time import sleep
from rich.columns import Columns
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
import pandas as pd
from dateutil import parser
"""
This example shows how to display content in columns.

The data is pulled from https://randomuser.me
"""

from rich.spinner import Spinner

from rich.console import Console
from rich.columns import Columns
from rich.panel import Panel
from rich.table import Table


from rich import box
from rich.console import Console
from rich.live import Live
from rich.table import Table


def calculate_cpu_percent(d):
    try:
        cpu_count = len(d["cpu_stats"]["cpu_usage"]["percpu_usage"])
        cpu_delta = float(d["cpu_stats"]["cpu_usage"]["total_usage"]) - \
                    float(d["precpu_stats"]["cpu_usage"]["total_usage"])
        system_delta = d["cpu_stats"]["cpu_usage"]["total_usage"]
        assert system_delta > 0.0
        cpu_percent = cpu_delta / system_delta * 100.0 * cpu_count
    except:
        cpu_percent = -1.0
    return '{0:.2f}'.format(cpu_percent)

def calculate_memory_percent(d):
    try:
        mem_used = d["memory_stats"]["max_usage"]/d["memory_stats"]["limit"]
    except:
        mem_used = -1.0
    return '{0:.2f}'.format(mem_used)
    
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
        return Columns(panels, title="Dev" if self._is_dev else "Prod")
    
    
    @staticmethod
    def make_panel(container, stat):
        state = container["info"].attrs["State"]["Status"]
        IP = container["info"].attrs["NetworkSettings"]["IPAddress"]
        if IP == "":
            IP = "0.0.0.0"
        cpu = calculate_cpu_percent(stat)
        mem = calculate_memory_percent(stat)
        iu,ou = "MB", "MB"
        try:
            i = stat["networks"]["eth0"]["rx_bytes"]
            if i<pow(10,9):
                i /= pow(10,6)
            else:
                i /= pow(10,9)
                iu = "GB"
            i = format(i, '.2f')
            
            o = stat["networks"]["eth0"]["tx_bytes"]
            if o<pow(10,9):
                o /= pow(10,6)
            else:
                o /= pow(10,9)
                ou = "GB"    
            o = format(o, '.2f')
        except:
            i, o = 0, 0
        color_state = "yellow" if not state=="running" else "green"
        cpu_color = "blue" if int(eval(cpu))<70 else "yellow"
        mem_color = "blue" if int(eval(mem))<70 else "yellow"
        delta = None
        try:
            d0 = parser.parse(container["info"].attrs["State"]["StartedAt"]).replace(tzinfo=timezone.utc)
            d1 = datetime.now(timezone.utc)
            delta = timedelta(seconds=(d1-d0).seconds)
        except:
            pass
        return f"[{color_state}]{state} ({delta})\n" \
            f"[{'purple'}]IP: {IP}\n" \
            f"[{cpu_color}]CPU [{cpu}]\n" \
            f"[{mem_color}]MEM [{mem}]\n" \
            f"NET [{i}{iu}/{o}{ou}]\n" \
                




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
                        ports.append(f"{v[0]['HostPort']}:{k}")
                    else:
                        ports.append(f"{k}")
                d["Ports"]= "\n".join(ports)
            except:
                pass
            try:
                mounts=[]
                for m in c.attrs['Mounts']:
                    mounts.append(f"{m['Source']}:{m['Destination']}")
                d["Mounts"]= "\n".join(sorted(mounts))
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
    Layout(name="header",   size=2),
    Layout(name="stats",
           minimum_size=10,
           ratio=1,
           ),
    Layout(name="containers",
           minimum_size=10,
        ratio=2
           ),

)

layout["stats"].split_row(
    Layout(name="dev_containers"),
    Layout(name="prod_containers",
        #    ratio=2
           )
    )

# layout["containers"].update(
#     Align.center(
#         Text(
#             """This is a demonstration of rich.Layout\n\nHit Ctrl+C to exit""",
#             justify="center",
#         ),
#         vertical="middle",
#     )
# )


class Clock:
    """Renders the time in the center of the screen."""

    def __rich__(self) -> Text:
        return Text(datetime.now().ctime(), style="bold magenta", justify="center")
client = docker.from_env()

containers = client.containers.list()

layout["header"].update(Clock())
layout["prod_containers"].update(DockerColumns(client, is_dev=False))
layout["containers"].update(DockerTable(client, full=False))
layout["dev_containers"].update(DockerColumns(client, is_dev=True))

with Live(layout, screen=True, redirect_stderr=False) as live:
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
