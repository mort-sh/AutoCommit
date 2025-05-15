from pathlib import Path
import sys
import tomllib

from rich.console import Console
from rich.table import Table


def list_project_scripts():
    """Reads pyproject.toml from the project root and lists the defined scripts in a formatted table."""
    console = Console()
    pyproject_path = Path("pyproject.toml")

    if not pyproject_path.is_file():
        console.print(f"[red]Error: {pyproject_path} not found in the current directory.[/red]")
        console.print("[red]Please run this script from the project root.[/red]")
        sys.exit(1)

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        console.print(f"[red]Error parsing {pyproject_path}: {e}[/red]")
        sys.exit(1)
    except OSError as e:
        console.print(f"[red]Error reading {pyproject_path}: {e}[/red]")
        sys.exit(1)

    scripts = data.get("project", {}).get("scripts", {})

    console.print("\n[bold cyan underline]Defined Project Scripts[/bold cyan underline]\n")
    if not scripts:
        console.print("[yellow]  (None)[/yellow]")
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Script Name", style="dim", width=30)
        table.add_column("Target", style="dim")

        for name, target in sorted(scripts.items()):  # Sort alphabetically for consistent output
            table.add_row(name, target)

        console.print(table)


def main():
    """Entry point for the script. Calls the function to list scripts."""
    list_project_scripts()


if __name__ == "__main__":
    main()
