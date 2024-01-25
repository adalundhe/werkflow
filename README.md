# Werkflow

Werkflow is a CLI tool for creating environments for composing and executing workflows, authored as directed acrylic graphs. Werkflow provides a suite of integrations called *modules* to help in automating complex tasks, as well as the ability to extend Werkflow by writing your own.

# Why Werkflow?

Local setup, security maintenance, database migrations - all of these are examples of work that is repetitive, complex, and time consuming large amounts of time for developers and teams. Werkflow aims to make these this work easier by combining friendly automation with reproducable, concurrent workflows.

```python
# Migrate SQL Script
import os
import sqlalchemy
from werkflow import (
    Workflow,
    step,
    requires
)
from werkflow_mysql import MySQL # Via the werkflow-mysql python package.


@requires(MySQL)
class MigrateSQLDatabase(Workflow):
    sql=MySQL()

    @step()
    async def connect_to_database(self):

        username = os.getenv("SQL_USERNAME")
        password = os.getenv("SQL_PASSWORD")

        await self.sql.connect(
            location=f"mysql://{username}:{password}@localhost:5432/mydb"
        )

    @step("connect_to_database")
    async def get_existing_table_definition(self):
        return {
            "columns": await self.sql.table.get_columns("old_table")
        }

    @step("get_existing_table_definition")
    async def create_target_table(
        self,
        columns: List[sqlalchemy.Column]=[]
    ):
        await self.sql.table.create(
            "new_table",
            columns=[
                *columns,
                sqlalchemy.Column("my_new_column", sqlalchemy.Text)
            ]
        )

    @step("create_target_table")
    async def get_current_table_data(self):
        return {
            "records": await self.sql.select(
                table="old_table",
                columns=["*"]
            )
        }

    @step("get_current_table_data")
    async def insert_new_table_data(
        self,
        records: List[Dict[str, Any]]=[]
    ):
        await self.batch(
            self.sql.insert(
                table="new_table",
                values={
                    **record,
                    "my_new_column": "Some new data."
                }
            ) for record in records
        )

    @step("insert_new_table_data")
    async def close_session(self):
        await self.sql.close()

```


Werkflow also comes with a comprehensive API for adding interactivity to your workflows, allowing workflows to be reused and adapted to changing needs and requirements:

```python
import sqlalchemy
from werkflow import (
    Workflow,
    step,
    requires
)
from werkflow_mysql import MySQL # Via the werkflow-mysql python package.
from werkflow.prompt import (
    InputPrompt,
    SecurePrompt
)


@requires(MySQL)
class MigrateSQLDatabase(Workflow):
    sql=MySQL()

    @step(
        prompts=[
            InputPrompt(
                message="What's the username you'd like to use?",
                result_key='sql_username',
                default=os.getenv("SQL_USERNAME"),
                confirmation_message=lambda table_name: f"Got {table_names}!"
            ),
            # This won't be echoed to stdout.
            SecurePrompt(
                message="What's the password for this user?",
                result_key='sql_password',
                default=os.getenv("SQL_PASSWORD"),
                confirmation_message="Got it!"
            ),
            InputPrompt(
                message="What's the database?",
                result_key='sql_database',
                default=os.getenv("SQL_DATABASE"),
                confirmation_message=lambda database_name: f"Got {database_name}!"
            ),
        ]
    ):
    async def connect_to_database(
        self,
        sql_username: str=None,
        sql_password: str=None,
        sql_database: str=None
    ):
        await self.sql.connect(
            location=f"mysql://{sql_username}:{sql_password}@localhost:5432/{sql_database}"
        )

    @step(
        prompts=[
            InputPrompt(
                message="What's the name of the existing table?",
                result_key='existing_table_name',
                confirmation_message=lambda table_name: f"Got {table_names}!"
            ),
            InputPrompt(
                message="What's the name of the new table?",
                result_key='new_table_name',
                confirmation_message=lambda table_name: f"Got {table_name}!"
            ),
        ]
    )
    async def get_existing_table_definition(
        self,
        existing_table_name: str=None
    ):
        return {
            "columns": await self.sql.table.get_columns(
                table=existing_table_name
            )
        }

    @step("get_existing_table_definition")
    async def create_target_table(
        self,
        new_table_name: str=None,
        columns: List[sqlalchemy.Column]=[]
    ):
        await self.sql.table.create(
            table=new_table_name,
            columns=[
                *columns,
                sqlalchemy.Column("my_new_column", sqlalchemy.Text)
            ]
        )

    @step("create_target_table")
    async def get_current_table_data(
        self,
        # Once input is received you can access that data anywhere in the workflow!
        existing_table_name: str=None
    ):
        return {
            "records": await self.sql.select(
                table=existing_table_name,
                columns=["*"]
            )
        }

    @step("get_current_table_data")
    async def insert_new_table_data(
        self,
        new_table_name: str=None,
        records: List[Dict[str, Any]]=[]
    ):
        await self.batch(
            self.sql.insert(
                table=new_table_name,
                values={
                    **record,
                    "my_new_column": "Some new data."
                }
            ) for record in records
        )

    @step("insert_new_table_data")
    async def close_session(self):
        await self.sql.close()

```

Interactivity can also be bypassed and a `.werkflow.json` file used instead:

```json
{
    "project_name": "migrate-db",
    "project_path": "/Users/myuser/Documents/migration-scripts",
    "project_scripts": [],
    "project_type": "mysql",
    "project_options": {
        "sql_username": "mysqluser",
        "sql_database": "mydb",
        "existing_table_name": "my_old_table",
        "new_table_name": "my_new_table"
    }
}
```

as well as all-caps environmental variables names:

```
export SQL_PASSWORD="mysupersecretpassword"
```


# Installation and Getting Started

Werkflow is a pip installable package! We recommend using Python virtual environments, with Python 3.10+:

```
python -m venv ~/.werkflow && \
pip install werkflow
```

Then run:

```
werkflow --help
```

to verify everything's working correctly!


# My First Workflow

To get started, we're going to create a workflow that:

1. Creates a new directory and text file in that directory.
2. Pipes "Hello world!" to that file.
3. Reads in that file and outputs the stored message via Werkflow's logging.

Begin by creating an empty Python file:

```bash
touch myworkflow.py
```

Open the file and import the following:

```python
from werkflow import Workflow
```

For Werkflow, workflows must be specified as Python classes that inherit from the base `Workflow` class. Go ahead and
add a Python class like below without any methods or attributes:


```python
from werkflow import Workflow


class MyFirstWorkflow(Workflow):
    pass
```

The workflow we've created isn't doing us much good as any empty class. We need to add asynchronous methods wrapped with the `step` decorator in order to start doing anything! Let's go ahead and import the `step` decorator and use it to wrap an empty class method:

```python
from werkflow import Workflow, step


class MyFirstWorkflow(Workflow):
    
    @step()
    async def create_new_directory(self):
        pass

```

We can verify our Graph works by running:

```
werkflow workflow run <path_to_my_workflow>.py
```

Now let's get started on our first task - creating an empty directory and new file within it! Werkflow comes with pre-written integrations to help you accomplish common tasks. One of these integrations is a wrapper around your operating system's shell module, and it's provided by default with the base `Workflow` class your new workflow inherits from!

In this instance, we'll be using the Shell module's `create_directory()` method within a `step`-wrapped asynchronous method (which we'll refer to from here on as a step):

```python
from werkflow import Workflow, step


class MyFirstWorkflow(Workflow):
    
    @step()
    async def create_new_directory(self):
        directory_path = "./my_new_directory"
        await self.shell.create_directory(directory_path)

```

Go ahead and re-run the workflow. This time, you should see a new `/my_new_directory` folder is created!

Next we need to create an empty file. We'll add a second step and use the Shell module to accomplish this:

```python
from werkflow import Workflow, step


class MyFirstWorkflow(Workflow):
    
    @step()
    async def create_new_directory(self):
        directory_path = "./my_new_directory"
        await self.shell.create_directory(directory_path)

    @step()
    async def create_file(self):
        await self.shell.touch("my_new_file.txt")

```

Re-run the graph again. Oh no! Our new file was created but not in the right directory! Likewise, it looks like the steps were run at the same time! This is intentional and an important part of Werkflow's execution - __steps that can be executed concurrently, i.e. without dependencies on each other or previous steps that would prevent them from executing concurrently, will execute concurrently__. This is one of the primary the reasons step methods are asynchronous.

To remedy this issue, we need to specify that the `create_file()` step *depends* upon the `create_new_directory()` step. To do this, we must pass the name of the precending __dependent__ step as a positional argument to the `step` hook:

```python
from werkflow import Workflow, step


class MyFirstWorkflow(Workflow):
    
    @step()
    async def create_new_directory(self):
        directory_path = "./my_new_directory"
        await self.shell.create_directory(directory_path)

    @step("create_new_directory")
    async def create_file(self):
        await self.shell.touch("my_new_file.txt")

```

Re-run the graph again. Excellent! The steps are no longer executing at the same time. However, our file is still being created in the wrong directory. We could simply hardcode the new directory as part of the path passed to the Shell module's `touch()` method, but there's a second means.

Add a return statement to the `create_new_directory()` step, returning a dictionary with the key being `directory_path` and value being the `directory_path` local variable within the step. Then, add `directory_path` as a keyword argument to the `create_file()` step, and use your preferred method of string formatting to append it to the path passed to the Shell module's `touch()` method:

```python
import os
from werkflow import Workflow, step


class MyFirstWorkflow(Workflow):
    
    @step()
    async def create_new_directory(self):
        directory_path = "./my_new_directory"
        await self.shell.create_directory(directory_path)

        return {
            'directory_path': directory_path
        }

    @step("create_new_directory")
    async def create_file(
        self,
        directory_path: str="./"
    ):

        new_file_path = os.path.join(
            directory_path,
            "my_new_file.txt"
        )

        await self.shell.touch(new_file_path)

```

Steps pass state from one to the next using `Context`, a workflow-wide key/value store that persists only for the duration of the workflow's execution. You may add to a workflow's Context by returning a Python dictionary of Context Keys and Context Values, which will then be made available to any subsequent dependent steps.

__*Note*__: You can also return non-dictionary values from steps, which are stored in Context under the name of the step.


Let's re-run our workflow. Excellent! The file is now created within the new folder. Let's continue and add another step, which will write our message to the new file. As above, we'll want to store our new file's path in the workflow's Context, passing it to this new step so the message can be written to the correct file. We'll be using the Shell module's `pipe_to_file()` method in this step:

```python
import os
from werkflow import Workflow, step


class MyFirstWorkflow(Workflow):
    
    @step()
    async def create_new_directory(self):
        directory_path = "./my_new_directory"
        await self.shell.create_directory(directory_path)

        return {
            'directory_path': directory_path
        }

    @step("create_new_directory")
    async def create_file(
        self,
        directory_path: str="./"
    ):

        new_file_path = os.path.join(
            directory_path,
            "my_new_file.txt"
        )

        await self.shell.touch(new_file_path)

        return {
            "new_file_path": new_file_path
        }

    @step("create_file")
    async def write_message_to_file(
        self,
        new_file_path: str=None
    ):
        if new_file_path:
            await self.shell.pipe_to_file(
                new_file_path,
                "Hello world!",
                silent=True
            )

```

Re-run the graph, and then open the file. You should see:

```
Hello world!
```

Excellent! By using Context, we can quickly and easily pass state between steps without polluting the class attributes of our workflow or having to use global scope. Finally, let's read in the data from our created file and then print it out using Werkflow's powerful logging system.

Add a final step as below, which takes in the new file path from context, uses the Shell module's `read_file()` method to read in our message, and then prints the message to stdout via the `WerkflowLogger` instance included in every workflow.

```python
import os
from werkflow import Workflow, step


class MyFirstWorkflow(Workflow):
    
    @step()
    async def create_new_directory(self):
        directory_path = "./my_new_directory"
        await self.shell.create_directory(directory_path)

        return {
            'directory_path': directory_path
        }

    @step("create_new_directory")
    async def create_file(
        self,
        directory_path: str="./"
    ):

        new_file_path = os.path.join(
            directory_path,
            "my_new_file.txt"
        )

        await self.shell.touch(new_file_path)

        return {
            "new_file_path": new_file_path
        }

    @step("create_file")
    async def write_message_to_file(
        self,
        new_file_path: str=None
    ):
        if new_file_path:
            await self.shell.pipe_to_file(
                new_file_path,
                "Hello world!",
                silent=True
            )

    @step("write_message_to_file")
    async def read_and_log_message(
        self,
        new_file_path: str=None
    ):
        if new_file_path:
            message = await self.shell.read_file(
                new_file_path,
                silent=True
            )
                 
            await self.logger.spinner.append_message(message)

```

Re-run the workflow as before. Note that our message now cycles through via Werkflow's CLI GUI! When logging output that is not system critical, we recommend appending the output to "spinner" as opposed to directly logging to console. However, if you need to log import system information to console, simply change the call above to:

```python
await self.logger.console.aio.info(message)
```

Werkflow's logging includes both synchronous and asynchronous logging for console and files. When logging information in any workflow, you should __always__ use the asynchronous variant.

Congratulations! You've just written your first workflow!