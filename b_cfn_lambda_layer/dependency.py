from typing import Optional

from b_cfn_lambda_layer.package_version import PackageVersion


class Dependency:
    def __init__(self, name: str, version: Optional[PackageVersion] = None):
        self.__name = name
        self.__version = version or PackageVersion.latest()

    def build_string(self) -> str:
        """
        Creates string representation of the dependency that can be used by PIP tool.

        For example, if you initiate this class:
        >>> dep = Dependency('jwt', PackageVersion.from_string_version('123'))
        Then when you execute this method, you will get:
        >>> dep.build_string() == 'jwt==123'

        :return: String representation.
        """
        if self.__version.version_type == PackageVersion.VersionType.LATEST:
            return self.__name

        if self.__version.version_type == PackageVersion.VersionType.SPECIFIC:
            return f'{self.__name}=={self.__version.version_string}'

        if self.__version.version_type == PackageVersion.VersionType.NONE:
            return ''

        else:
            raise ValueError('Unsupported enum value.')
