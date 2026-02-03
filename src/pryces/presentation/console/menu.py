"""Interactive menu system for console commands."""

import sys
from typing import TextIO

from .commands.base import Command, InputPrompt
from .commands.registry import CommandRegistry


class InteractiveMenu:
    """Interactive menu for selecting and executing console commands."""

    def __init__(
        self,
        registry: CommandRegistry,
        input_stream: TextIO = sys.stdin,
        output_stream: TextIO = sys.stdout
    ) -> None:
        """Initialize the interactive menu."""
        self._registry = registry
        self._input = input_stream
        self._output = output_stream

    def run(self) -> None:
        """Run the interactive menu loop."""
        while True:
            self._display_menu()

            selection = self._get_selection()

            if selection == 0:
                self._output.write("\nGoodbye!\n")
                break

            commands = self._registry.get_all_commands()
            if 1 <= selection <= len(commands):
                command = commands[selection - 1]
                self._execute_command(command)
            else:
                self._output.write(f"\nInvalid selection: {selection}\n")

            self._output.write("\n")

    def _display_menu(self) -> None:
        """Display the menu of available commands."""
        commands = self._registry.get_all_commands()

        self._output.write("\n" + "=" * 60 + "\n")
        self._output.write("PRYCES - Stock Price Information System\n")
        self._output.write("=" * 60 + "\n\n")
        self._output.write("Available Commands:\n\n")

        for idx, command in enumerate(commands, start=1):
            metadata = command.get_metadata()
            self._output.write(f"  {idx}. {metadata.name}\n")
            self._output.write(f"     {metadata.description}\n\n")

        self._output.write(f"  0. Exit\n\n")
        self._output.flush()

    def _get_selection(self) -> int:
        """Get and validate user's menu selection."""
        while True:
            try:
                self._output.write("Enter your selection: ")
                self._output.flush()

                line = self._input.readline()
                if not line:
                    return 0

                line = line.strip()
                if not line:
                    continue

                selection = int(line)
                return selection

            except ValueError:
                self._output.write("Invalid input. Please enter a number.\n")
                self._output.flush()
            except EOFError:
                return 0

    def _execute_command(self, command: Command) -> None:
        """Execute a command after collecting required inputs."""
        metadata = command.get_metadata()
        self._output.write(f"\n--- {metadata.name} ---\n\n")

        inputs = self._collect_inputs(command.get_input_prompts())

        if inputs is None:
            self._output.write("\nCommand cancelled.\n")
            return

        self._output.write("\nExecuting...\n\n")

        try:
            result = command.execute(**inputs)
            self._output.write(result)
            self._output.write("\n")
        except Exception as e:
            self._output.write(f"\nError executing command: {e}\n")

        self._wait_for_keypress()

    def _wait_for_keypress(self) -> None:
        """Wait for user to press any key before continuing."""
        self._output.write("\nPress Enter to continue...")
        self._output.flush()
        self._input.readline()

    def _collect_inputs(self, prompts: list[InputPrompt]) -> dict | None:
        """Collect inputs from user based on prompts."""
        inputs = {}

        for prompt in prompts:
            while True:
                self._output.write(prompt.prompt)
                self._output.flush()

                try:
                    value = self._input.readline()

                    if not value:
                        return None

                    value = value.strip()
                    if not value:
                        self._output.write("Input cannot be empty. Try again.\n")
                        continue

                    if prompt.validator and not prompt.validator(value):
                        self._output.write("Invalid input format. Try again.\n")
                        continue

                    inputs[prompt.key] = value
                    break

                except EOFError:
                    return None

        return inputs
