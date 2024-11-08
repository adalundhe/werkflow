import os

from werkflow import Workflow, step


class BasicWerkflow(Workflow):

    @step()
    async def list_files_in_current_directory(self):
        current_directory = await self.shell.get_current_directory()
        return {
            'current_directory': current_directory,
            'directory_files': await self.file.list_matching_files(
                current_directory,
                '*'
            )
        }
    
    @step('list_files_in_current_directory')
    async def sort_files_and_print_names(
        self,
        directory_files: list[str] = []
    ):
        sorted_files = sorted(directory_files)

        for file in sorted_files:
            await self.logger.spinner.info(f'Found file - {file}')

    @step('sort_files_and_print_names')
    async def cleanup_logs_and_pycache(
        self,
        current_directory: str
    ):
        await self.batch(
            self.shell.rm(
                os.path.join(
                    current_directory,
                    '__pycache__',
                ),
                silent=True,
            ),
            self.shell.rm(
                os.path.join(
                    current_directory,
                    'logs',
                ),
                silent=True,
            )
        )

            