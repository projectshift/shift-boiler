### Application CLI entrypoint.

Here we import and assemble our cli tool from other cli modules provided by application components. Basically we either use or create a project cli and then have an option to mount or merge-in additional commands or command groups.

For example:

```python

# mount single command:
module1.cli.add_command(module2.command)

# mount another cli as sub command
module1.cli.add_command(module2.cli, name='module2')

#merge commands from modules into single cli
merged_cli = click.CommandCollection(sources=[module1.cli, module2.cli])
```