"""Utility classes for writing XBlock unit tests.

These utilities use the workbench runtime to load XML scenarios.
"""


import json
from functools import wraps

import webob

from workbench.runtime import WorkbenchRuntime


def scenario(scenario_path, user_id=None):
    """
    Method decorator to load a scenario for a test case.
    Must be called on an `XBlockHandlerTestCase` subclass, or
    else it will have no effect.

    Args:
        scenario_path (str): Path to the scenario XML file.

    Keyword Arguments:
        user_id (str or None): User ID to log in as, or None.

    Returns:
        The decorated method

    Example:

        @scenario('data/test_scenario.xml')
        def test_submit(self, xblock):
            response = self.request(xblock, 'submit', 'Test submission')
            self.assertTrue('Success' in response)
    """
    def _decorator(func):
        """
        Decorate function to wrap the scenario
        """
        @wraps(func)
        def _wrapped(*args, **kwargs):
            """
            Load a scenario and pass it along to the method invocation
            """

            # Retrieve the object (self)
            # if this is a function, not a method, then do nothing.
            xblock = None
            if args:
                self = args[0]
                if isinstance(self, XBlockHandlerTestCaseMixin):
                    # Print a debug message
                    print(f"Loading scenario from {scenario_path}")

                    # Configure the runtime with our user id
                    self.set_user(user_id)

                    # Load the scenario
                    xblock = self.load_scenario(scenario_path)

                    # Pass the XBlock as the first argument to the decorated method (after `self`)
                    args = list(args)
                    args.insert(1, xblock)

            return func(*args, **kwargs)
        return _wrapped
    return _decorator


class XBlockHandlerTestCaseMixin:
    """Load the XBlock in the workbench runtime to test its handler. """

    def setUp(self):
        """Create the runtime. """
        super().setUp()
        self.runtime = WorkbenchRuntime()

    def set_user(self, user_id):
        """Provide a user ID to the runtime.

        Args:
            user_id (str): a user ID.

        Returns:
            None
        """
        self.runtime.user_id = user_id

    def load_scenario(self, xml_path):
        """Load an XML definition of an XBlock and return the XBlock instance.

        Args:
            xml (string): Path to an XML definition of the XBlock, relative
                to the test module.

        Returns:
            XBlock
        """
        block_id = self.runtime.parse_xml_string(
            self.load_fixture_str(xml_path), self.runtime.id_generator
        )
        return self.runtime.get_block(block_id)

    def request(self, xblock, handler_name, content, request_method="POST", response_format=None):
        """Make a request to an XBlock handler.

        Args:
            xblock (XBlock): The XBlock instance that should handle the request.
            handler_name (str): The name of the handler.
            content (unicode): Content of the request.

        Keyword Arguments:
            request_method (str): The HTTP method of the request (defaults to POST)
            response_format (None or str): Expected format of the response string.
                If `None`, return the raw response content; if 'json', parse the
                response as JSON and return the result.

        Raises:
            NotImplementedError: Response format not supported.

        Returns:
            Content of the response (mixed).
        """
        # Create a fake request
        request = webob.Request(dict())
        request.method = request_method
        request.body = content

        # Send the request to the XBlock handler
        response = self.runtime.handle(xblock, handler_name, request)

        # Parse the response (if a format is specified)
        if response_format is None:
            return response.body
        elif response_format == 'json':
            return json.loads(response.body)
        else:
            raise NotImplementedError(f"Response format '{response_format}' not supported")

    @staticmethod
    def load_fixture_str(path):
        """Load data from a fixture file.

        Args:
            path (str): Path to the file.

        Returns:
            unicode: contents of the file.
        """
        with open(path, 'rb') as file_handle:
            return file_handle.read()
