import sys
from typing import TextIO

from .commands.base import Command, InputPrompt
from .commands.registry import CommandRegistry


class InteractiveMenu:
    def __init__(
        self,
        registry: CommandRegistry,
        input_stream: TextIO = sys.stdin,
        output_stream: TextIO = sys.stdout,
    ) -> None:
        self._registry = registry
        self._input = input_stream
        self._output = output_stream

    def run(self) -> None:
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
            except EOFError:  # pragma: no cover
                return 0

    def _execute_command(self, command: Command) -> None:
        metadata = command.get_metadata()
        self._output.write(f"\n--- {metadata.name} ---\n")

        inputs = self._collect_inputs(command.get_input_prompts())

        if inputs is None:
            self._output.write("\nCommand cancelled.\n")
            return

        if metadata.show_progress:
            self._output.write("\nExecuting...\n")

        try:
            result = command.execute(**inputs)
            self._output.write(f"\n{result.message}\n")
        except Exception as e:
            self._output.write(f"\nError executing command: {e}\n")

        self._wait_for_keypress()

    def _wait_for_keypress(self) -> None:
        self._output.write("\nPress Enter to continue...")
        self._output.flush()
        self._input.readline()

    def _collect_inputs(self, prompts: list[InputPrompt]) -> dict | None:
        inputs = {}

        for prompt in prompts:
            self._output.write("\n")
            if prompt.preamble is not None:
                self._output.write(prompt.preamble + "\n")

            while True:
                self._output.write(prompt.prompt + "\n  (q to cancel) ")
                self._output.flush()

                try:
                    value = self._input.readline()

                    if not value:
                        return None

                    value = value.strip()

                    if value.lower() == "q":
                        return None

                    if not value:
                        if prompt.default is not None:
                            inputs[prompt.key] = prompt.default
                            break
                        self._output.write("Input cannot be empty. Try again.\n")
                        continue

                    if prompt.validator:
                        error = prompt.validator(value)
                        if error is not None:
                            self._output.write(f"{error} Try again.\n")
                            continue

                    inputs[prompt.key] = value
                    break

                except EOFError:  # pragma: no cover
                    return None

        return inputs
