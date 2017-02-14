import zipfile
from mock import patch
from pyfakefs import fake_filesystem_unittest
from tests.asserts import *
from shellfoundry.commands.pack_command import PackCommandExecutor


class TestPackCommandExecutor(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    @patch('click.echo')
    @patch('shellfoundry.utilities.python_dependencies_packager.pip')
    def test_build_package_package_created(self, pip_mock, echo_mock):
        # Arrange
        self.fs.CreateFile('nut_shell/shell.yml', contents="""
shell:
    name: nut_shell
    author: Chuck Norris
    email: chuck@hollywood.io
    description: Save the world
    version: 1.0.0
    driver_name: nutshell
    """)
        self.fs.CreateFile('nut_shell/datamodel/metadata.xml')
        self.fs.CreateFile('nut_shell/datamodel/datamodel.xml')
        self.fs.CreateFile('nut_shell/datamodel/shellconfig.xml')
        self.fs.CreateFile('nut_shell/src/driver.py')
        os.chdir('nut_shell')

        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()

        # Assert
        assertFileExists(self, 'dist/nut_shell.zip')
        TestPackCommandExecutor.unzip('dist/nut_shell.zip', 'dist/nut_shell')
        TestPackCommandExecutor.unzip('dist/nut_shell/Resource Drivers - Python/nutshell.zip', 'dist/nutshell')
        assertFileDoesNotExist(self, 'dist/nutshell/debug.xml')

        echo_mock.assert_any_call(u'Shell package was successfully created:')

    @patch('click.echo')
    @patch('shellfoundry.utilities.python_dependencies_packager.pip')
    def test_build_package_debugmode_package_created_with_debug_file(self, pip_mock, echo_mock):
            # Arrange
            self.fs.CreateFile('nut_shell/shell.yml', contents="""
    shell:
        name: nut_shell
        author: Chuck Norris
        email: chuck@hollywood.io
        description: Save the world
        version: 1.0.0
        driver_name: nutshell
        """)
            self.fs.CreateFile('nut_shell/datamodel/metadata.xml')
            self.fs.CreateFile('nut_shell/datamodel/datamodel.xml')
            self.fs.CreateFile('nut_shell/datamodel/shellconfig.xml')
            self.fs.CreateFile('nut_shell/src/driver.py')
            os.chdir('nut_shell')

            command_executor = PackCommandExecutor()

            # Act
            command_executor.pack(debugmode=True)

            # Assert
            assertFileExists(self, 'dist/nut_shell.zip')
            TestPackCommandExecutor.unzip('dist/nut_shell.zip', 'dist/nut_shell')
            TestPackCommandExecutor.unzip('dist/nut_shell/Resource Drivers - Python/nutshell.zip', 'dist/nutshell')
            assertFileExists(self, 'dist/nutshell/debug.xml')

            echo_mock.assert_any_call(u'Shell package was successfully created:')

    @patch('click.echo')
    @patch('shellfoundry.utilities.python_dependencies_packager.pip')
    def test_proper_error_message_displayed_when_shell_yml_is_in_wrong_format(self, pip_mock, echo_mock):
        # Arrange
        self.fs.CreateFile('nut_shell/shell.yml', contents='WRONG YAML FORMAT')
        os.chdir('nut_shell')

        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()

        # Assert
        echo_mock.assert_any_call(u'shell.yml format is wrong')

    @patch('click.echo')
    @patch('shellfoundry.utilities.python_dependencies_packager.pip')
    def test_proper_error_message_displayed_when_shell_yml_missing(self, pip_mock, echo_mock):
        # Arrange
        self.fs.CreateFile('nut_shell/datamodel/datamodel.xml')
        os.chdir('nut_shell')

        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()

        # Assert
        echo_mock.assert_any_call(u'shell.yml file is missing')

    @patch('shellfoundry.commands.pack_command.ShellPackageBuilder.pack')
    def test_tosca_based_shell_packager_called_when_shell_contains_tosca_meta_file(self, pack_mock):
        # Arrange
        self.fs.CreateFile('nut-shell/TOSCA-Metadata/TOSCA.meta',
                           contents='TOSCA-Meta-File-Version: 1.0 \n'
                                    'CSAR-Version: 1.1 \n'
                                    'Created-By: Anonymous \n'
                                    'Entry-Definitions: shell-definition.yml')

        self.fs.CreateFile('nut-shell/shell-definition.yml',
                           contents='SOME SHELL DEFINITION')

        os.chdir('nut-shell')

        command_executor = PackCommandExecutor()

        # Act
        command_executor.pack()

        # Assert
        self.assertTrue(pack_mock.called)

    @staticmethod
    def unzip(source_filename, dest_dir):
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        with zipfile.ZipFile(source_filename) as zf:
            zf.extractall(dest_dir)
