from typing import Optional, Dict

from b_cfn_lambda_layer.package_version import PackageVersion


class PipInstall:
    def __init__(
            self,
            dependencies: Optional[Dict[str, PackageVersion]] = None,
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
        self.__dependencies = dependencies
        self.__additional_pip_install_args = additional_pip_install_args
        self.__output_directory = output_directory

    def build_command(self) -> str:
        install_commands = []

        # Create install commands for each dependency.
        for key, value in self.__dependencies.items():
            install_commands.append(self.__create_install_dependency_command(
                dependency=key,
                dependency_version=value,
                install_args=self.__additional_pip_install_args,
                output_dir=self.__output_directory,
            ))

        return ' & '.join(install_commands)

    @staticmethod
    def __create_install_dependency_command(
            dependency: str,
            dependency_version: Optional[PackageVersion] = None,
            install_args: Optional[str] = None,
            output_dir: Optional[str] = None
    ) -> str:
        """
        Creates a "pip install" command for specific dependency (package).

        :param dependency: Dependency name e.g. 'jwt'.
        :param dependency_version: Dependency version.
        :param install_args: Additional installation arguments for pip.
        :param output_dir: Directory where dependencies should be installed.

        :return: Install command as a string.
        """
        version = dependency_version or PackageVersion(version_type=PackageVersion.VersionType.LATEST)
        install_args = install_args or ''

        if version.version_type == PackageVersion.VersionType.LATEST:
            command = f'pip install {dependency} {install_args}'

        elif version.version_type == PackageVersion.VersionType.SPECIFIC:
            command = f'pip install {dependency}=={version.version_string} {install_args}'

        elif version.version_type == PackageVersion.VersionType.NONE:
            command = ''

        else:
            raise ValueError('Unsupported enum value.')

        if command and output_dir:
            command = f'{command} -t {output_dir}'

        return command
