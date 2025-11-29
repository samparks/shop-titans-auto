import click

from game_automator.workflows import discover_workflows


@click.group()
def main():
    """Game Automator - Automated workflows for Shop Titans."""
    pass


@main.command()
def list():
    """List available workflows."""
    workflows = discover_workflows()
    
    if not workflows:
        click.echo("No workflows found.")
        return
    
    click.echo("Available workflows:\n")
    for name, workflow_class in sorted(workflows.items()):
        click.echo(f"  {name:20} {workflow_class.description}")


@main.command()
@click.argument("workflow_name")
def run(workflow_name: str):
    """Run a workflow by name."""
    workflows = discover_workflows()
    
    if workflow_name not in workflows:
        click.echo(f"Unknown workflow: {workflow_name}")
        click.echo(f"Run 'game-automator list' to see available workflows.")
        return
    
    workflow_class = workflows[workflow_name]
    workflow = workflow_class()
    
    success = workflow.execute()
    
    if success:
        click.echo("\nDone!")
    else:
        click.echo("\nWorkflow did not complete successfully.")


@main.command()
def hotkey():
    """Start hotkey listener mode."""
    from game_automator.hotkey import main as hotkey_main
    hotkey_main()


if __name__ == "__main__":
    main()