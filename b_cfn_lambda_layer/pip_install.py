from typing import Optional, List

from b_cfn_lambda_layer.dependency import Dependency


class PipInstall:
    def __init__(
            self,
            dependencies: Optional[List[Dependency]] = None,
            additional_pip_install_args: Optional[str] = None,
            output_directory: Optional[str] = None
    ) -> None:
        """
        Constructor.

        :param dependencies: A dictionary of dependencies to be included within "pip install" command.
            Warning! The dependency strings are prone to code injections!
        :param additional_pip_install_args: A string of additional "pip install" command flags and arguments.
            Warning! This string is prone to code injections!
        """
        self.__dependencies = dependencies or []
        self.__additional_pip_install_args = additional_pip_install_args
        self.__output_directory = output_directory

    def build_command(self) -> str:
        command = ' '.join([dep.build_string() for dep in self.__dependencies if dep.build_string()])

        if command and self.__output_directory:
            command = f'{command} -t {self.__output_directory}'

        if command and self.__additional_pip_install_args:
            command = f'{command} {self.__additional_pip_install_args}'

        if command:
            # If dependencies are given, the "pip install" command will be built.
            command = f'pip install {command}'
        else:
            # If no dependencies are given, a simple "pip list" command is built.
            command = 'pip list'

        return command
