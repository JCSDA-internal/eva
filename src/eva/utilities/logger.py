# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------


import os
import sys
import traceback


# --------------------------------------------------------------------------------------------------


class textcolors:

    """
    A class that defines color codes for text in the terminal.
    """

    red = '\033[91m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    end = '\033[0m'

# --------------------------------------------------------------------------------------------------


class Logger:

    """
    Class providing logging functionality for tasks.
    """

    def __init__(self, task_name):

        """
        Initialize the Logger object.

        Args:
            task_name (str): The name of the task associated with the logger.

        Returns:
            None
        """

        self.task_name = task_name

        # Set default logging levels
        self.loggerdict = {"INFO": True,
                           "TRACE": False,
                           "DEBUG": False}

        # Loop over logging levels
        for loglevel in self.loggerdict:

            # Check for environment variable e.g. LOG_TRACE=1 will activiate trace logging
            log_env = os.environ.get('LOG_'+loglevel)

            # If found set element to environment variable
            if log_env is not None:
                self.loggerdict[loglevel] = int(log_env) == 1

        # Text colors
        self.tc = textcolors()

    # ----------------------------------------------------------------------------------------------

    def send_message(self, level, message):

        """
        Print a log message at the specified logging level.

        Args:
            level (str): The logging level for the message.
            message (str): The log message to be printed.

        Returns:
            None
        """

        if level.upper() == 'ABORT' or self.loggerdict[level]:
            prepend = level+' '+self.task_name+': '
            message = prepend + message.replace('\n', '\n'+prepend)
            print(message)

    # ----------------------------------------------------------------------------------------------

    def info(self, message):

        """
        Print an informational log message.

        Args:
            message (str): The informational log message.

        Returns:
            None
        """

        self.send_message("INFO", message)

    # ----------------------------------------------------------------------------------------------

    def trace(self, message):

        """
        Print a trace log message.

        Args:
            message (str): The trace log message.

        Returns:
            None
        """

        self.send_message("TRACE", message)

    # ----------------------------------------------------------------------------------------------

    def debug(self, message):

        """
        Print a debug log message.

        Args:
            message (str): The debug log message.

        Returns:
            None
        """

        self.send_message("DEBUG", message)

    # ----------------------------------------------------------------------------------------------

    def abort(self, message):

        """
        Print an abort log message and exit the program.

        Args:
            message (str): The abort log message.

        Returns:
            None
        """

        # Make the text red
        message = self.tc.red + message + self.tc.end

        self.send_message('ABORT', message)

        # Get traceback stack (without logger.py lines)
        filtered_stack = [line for line in traceback.format_stack() if 'logger.py' not in line]

        # Remove everything after 'logger.assert_abort' in last element of filtered_stack
        filtered_stack[-1] = filtered_stack[-1].split('logger.assert_abort')[0]

        traceback_str = '\n'.join(filtered_stack)

        # Exit with traceback
        sys.exit('\nHERE IS THE TRACEBACK: \n----------------------\n\n' + traceback_str)

    # ----------------------------------------------------------------------------------------------

    def assert_abort(self, condition, message):

        if condition:
            return
        else:
            self.abort(message)

# --------------------------------------------------------------------------------------------------
