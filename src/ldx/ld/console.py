from dataclasses import dataclass
import logging
import typing
import inspect
from ldx.ld.ldattr import LDAttr
from ldx.ld_base.i_player import IConsole, SOptional
from ldx.ld_base.model_list2meta import List2Meta
from ldx.ld_base.model_record import Record
import ldx.ld_base.enums as E
from ldx.ld_base.batch_console_ext import BatchMixin
from ldx.utils.subprocess import open_detached, query


@dataclass
class Console(IConsole, BatchMixin):
    """
    A class for interacting with the LDPlayer console.
    """

    attr: LDAttr

    def list2(self) -> typing.List[List2Meta]:
        """
        Retrieves a list of List2Meta objects by querying the ldconsole_path with the "list2" command.

        Returns:
            typing.List[List2Meta]: A list of List2Meta objects representing the retrieved data.
        """
        res = query(self.attr.ldconsole, "list2")
        reslines = res.splitlines()
        return [
            List2Meta(
                **{
                    it[0]: it[1](v)
                    for it, v in zip(
                        List2Meta.__annotations__.items(), resline.split(",")
                    )
                }
            )
            for resline in reslines
        ]

    def globalsetting(
        self,
        fps: typing.Optional[int] = None,
        audio: typing.Optional[bool] = None,
        fastplay: typing.Optional[bool] = None,
        cleanmode: typing.Optional[bool] = None,
    ):
        """
        Sets global settings for the LDConsole.

        Args:
            fps (int, optional): The frames per second setting. Defaults to None.
            audio (bool, optional): Whether to enable audio. Defaults to None.
            fastplay (bool, optional): Whether to enable fast play. Defaults to None.
            cleanmode (bool, optional): Whether to enable clean mode. Defaults to None.

        Returns:
            LDConsole: The current LDConsole instance.
        """
        arglist = []
        if fps is not None:
            arglist.extend(["--fps", str(fps)])
        if audio is not None:
            arglist.extend(["--audio", 1 if audio else 0])
        if fastplay is not None:
            arglist.extend(["--fastplay", 1 if fastplay else 0])
        if cleanmode is not None:
            arglist.extend(["--cleanmode", 1 if cleanmode else 0])
        open_detached(self.attr.ldconsole, "globalsetting", *arglist)
        return self

    def modify(
        self,
        name: typing.Optional[typing.Optional[str]] = None,
        index: typing.Optional[typing.Optional[int]] = None,
        resolution: typing.Optional[str] = None,
        cpu: typing.Optional[typing.Literal[1, 2, 3, 4]] = None,
        memory: typing.Optional[
            typing.Literal[256, 512, 768, 1024, 2048, 4096, 8192]
        ] = None,
        manufacturer: typing.Optional[str] = None,
        model: typing.Optional[str] = None,
        pnumber: typing.Optional[int] = None,
        imei: typing.Optional[typing.Union[typing.Literal["auto"], str]] = None,
        imsi: typing.Optional[typing.Union[typing.Literal["auto"], str]] = None,
        simserial: typing.Optional[typing.Union[typing.Literal["auto"], str]] = None,
        androidid: typing.Optional[typing.Union[typing.Literal["auto"], str]] = None,
        mac: typing.Optional[typing.Union[typing.Literal["auto"], str]] = None,
        autorotate: typing.Optional[bool] = None,
        lockwindow: typing.Optional[bool] = None,
        root: typing.Optional[bool] = None,
    ):
        """
        Modifies the settings of an emulator instance.

        Args:
            name (str, optional): The name of the emulator instance to modify. Either name or index must be provided.
            index (int, optional): The index of the emulator instance to modify. Either name or index must be provided.
            resolution (str, optional): The screen resolution (e.g., "1920x1080").
            cpu (int, optional): The number of CPU cores (1, 2, 3, or 4).
            memory (int, optional): The amount of memory in MB (256, 512, 768, 1024, 2048, 4096, or 8192).
            manufacturer (str, optional): The device manufacturer name.
            model (str, optional): The device model name.
            pnumber (int, optional): The phone number.
            imei (str, optional): The IMEI number. Use "auto" to generate automatically.
            imsi (str, optional): The IMSI number. Use "auto" to generate automatically.
            simserial (str, optional): The SIM serial number. Use "auto" to generate automatically.
            androidid (str, optional): The Android ID. Use "auto" to generate automatically.
            mac (str, optional): The MAC address. Use "auto" to generate automatically.
            autorotate (bool, optional): Whether to enable auto-rotation.
            lockwindow (bool, optional): Whether to lock the window.
            root (bool, optional): Whether to enable root access.

        Raises:
            ValueError: If neither name nor index is provided.

        Returns:
            None
        """
        arglist = []
        if not name and not index:
            raise ValueError("Either name or index must be provided")
        if name is not None and isinstance(name, str):
            arglist.extend(["--name", name])
        else:
            arglist.extend(["--index", str(index)])

        if resolution is not None:
            arglist.extend(["--resolution", resolution])
        if cpu is not None:
            arglist.extend(["--cpu", str(cpu)])
        if memory is not None:
            arglist.extend(["--memory", str(memory)])
        if manufacturer is not None:
            arglist.extend(["--manufacturer", manufacturer])
        if model is not None:
            arglist.extend(["--model", model])
        if pnumber is not None:
            arglist.extend(["--pnumber", str(pnumber)])
        if imei is not None:
            arglist.extend(["--imei", str(imei)])
        if imsi is not None:
            arglist.extend(["--imsi", str(imsi)])
        if simserial is not None:
            arglist.extend(["--simserial", str(simserial)])
        if androidid is not None:
            arglist.extend(["--androidid", str(androidid)])
        if mac is not None:
            arglist.extend(["--mac", str(mac)])
        if autorotate is not None:
            arglist.extend(["--autorotate", 1 if autorotate else 0])
        if lockwindow is not None:
            arglist.extend(["--lockwindow", 1 if lockwindow else 0])
        if root is not None:
            arglist.extend(["--root", 1 if root else 0])
        open_detached(self.attr.ldconsole, "modify", *arglist)

    def operaterecord(
        self,
        name: str | None = None,
        index: int | None = None,
        content: str | Record | None = None,
    ):
        """
        Operates on a recorded script for an emulator instance.

        Args:
            name (str, optional): The name of the emulator instance. Either name or index must be provided.
            index (int, optional): The index of the emulator instance. Either name or index must be provided.
            content (str | Record, optional): The record content as a string or Record object. This parameter is required.

        Raises:
            AssertionError: If content is not provided.

        Returns:
            None
        """
        assert content is not None, "content is required"
        cmd = ["operaterecord"]
        if name is not None:
            cmd.extend(["--name", name])
        elif index is not None:
            cmd.extend(["--index", str(index)])
        if isinstance(content, Record):
            import json
            from dataclasses import asdict

            content = json.dumps(asdict(content))
        cmd.extend(["--content", content])
        open_detached(self.attr.ldconsole, *cmd)

    def __getattribute__(self, name: str):
        """
        Custom attribute access handler that enables batch execution for batchable commands.

        This method intercepts attribute access to wrap batchable commands with batch execution capabilities.
        When a batchable command is accessed, it returns a wrapper function that can handle both single
        and batch executions based on the provided arguments.

        Args:
            name (str): The name of the attribute being accessed.

        Returns:
            The requested attribute or a batch-enabled wrapper function for batchable commands.

        Raises:
            ValueError: If a batchable command is called without proper identification parameters
                       (name, index, instances filter, or console_func).
        """
        if name.startswith("_"):
            return super().__getattribute__(name)

        if name in E.BATCHABLE_COMMANDS:
            # Get the original method
            original_method = super().__getattribute__(name)
            
            # create wrapper to allow batch execution
            def batch_wrapper(*args, **kwargs):
                # Check if this is a batch call
                if self._is_batch_call(args, kwargs):
                    # Execute in batch mode
                    return self._execute_batch(name, *args, **kwargs)
                else:
                    # Standard validation for non-batch calls
                    if (
                        len(args) == 0
                        and kwargs.get("index", None) is None
                        and kwargs.get("name", None) is None
                        and 'instances' not in kwargs
                        and 'console_func' not in kwargs
                    ):
                        raise ValueError("Either name, index, list of targets, instances filter, or console_func must be provided")
                    
                    # Execute normally
                    return original_method(*args, **kwargs)
            
            return batch_wrapper
        
        # For non-batchable commands, return the original attribute
        return super().__getattribute__(name)


def _create_simple_exec_method(command: str):
    """
    Creates a simple execution method that runs a command without parameters.

    Args:
        command (str): The command name to execute.

    Returns:
        function: A method that executes the specified command.
    """
    def method(self) -> None:
        logging.info(f"Running exec command: {command}")
        open_detached(self.attr.ldconsole, command)

    return method


for se in E.SIMPLE_EXEC_LIST:
    setattr(Console, se, _create_simple_exec_method(se))


def _create_varied_method(func: typing.Callable, methodToUse: typing.Callable):
    """
    Creates a method that handles variable parameters based on function signature.

    This factory function creates methods that automatically parse function signatures
    and build command-line arguments from positional and keyword arguments. It handles
    special cases like name/index parameters and validates mandatory parameters.

    Args:
        func (Callable): The function whose signature defines the parameters.
        methodToUse (Callable): The method to execute (either open_detached or query).

    Returns:
        function: A dynamically created method that processes arguments and executes the command.
    """
    def method(self, *args, **kwargs):
        logging.info(f"Running exec command: {func.__name__}")

        # Start building the command list with the base command
        command_list = [func.__name__]

        # Get the signature of the function
        sig = inspect.signature(func)
        parameters = list(sig.parameters.values())

        # Check if 'name' and 'index' are in the parameters
        has_name_param = any(param.name == "name" for param in parameters)
        has_index_param = any(param.name == "index" for param in parameters)

        # Handle the special case of a single positional argument
        if len(args) == 1 and has_name_param and has_index_param:
            if "name" not in kwargs and isinstance(args[0], str):
                kwargs["name"] = args[0]
            elif "index" not in kwargs and isinstance(args[0], int):
                kwargs["index"] = args[0]
            else:
                # If the single argument does not match, treat it as a normal argument
                for i, arg in enumerate(args):
                    if i < len(parameters):
                        param_name = parameters[i].name
                        command_list.extend([f"--{param_name}", arg])
        else:
            # Handle multiple positional arguments
            for i, arg in enumerate(args):
                if i < len(parameters):
                    param_name = parameters[i].name
                    command_list.extend([f"--{param_name}", arg])

        # Handle keyword arguments
        for param in parameters[len(args) :]:
            param_name = param.name
            param_type = param.annotation

            if param_name in kwargs:
                param_value = kwargs[param_name]
                if param_value is not None:
                    command_list.extend([f"--{param_name}", param_value])
            else:
                if param_type is SOptional:
                    raise ValueError(f"Mandatory parameter '{param_name}' is missing")

        # Execute the command
        return methodToUse(self.attr.ldconsole, *command_list)

    return method


for ve in E.VARIED_EXEC_LIST:
    func = getattr(IConsole, ve)
    setattr(Console, ve, _create_varied_method(func, open_detached))


def _simple_query_method(command: str):
    """
    Creates a simple query method that runs a command and returns the output.

    Args:
        command (str): The command name to query.

    Returns:
        function: A method that executes the query and returns the result.
    """
    def method(self) -> None:
        logging.info(f"Running query command: {command}")
        return query(self.attr.ldconsole, command)

    return method


for sq in E.SIMPLE_QUERY_LIST:
    setattr(Console, sq, _simple_query_method(sq))

for eq in E.VARIED_QUERY_LIST:
    func = getattr(IConsole, eq)

    setattr(Console, eq, _create_varied_method(func, query))
