"""
This module will create Endpoint files from an OpenAPI spec ver 3.x

What does an Endpoint file hold?:
- It should contain a class with methods to make various http calls against an endpoint
- It should only contain steps to make the http calls and return the data
- It should not contain business logic

For more info read - https://qxf2.com/blog/easily-maintainable-api-test-automation-framework/

What does this module do?:
- It creates an Endpoint file with a class from the OpenAPI spec
- The path key in the spec is translated to an Endpoint
- The operations(http methods) for a path is translated to instance methods for the Endpoint
- The parameters for operations are translated to function parameters for the instance methods
- HTTP Basic, HTTP Bearer and API Keys Auth are currently supported by this module & handled through headers
"""


from openapi_parser import parse, specification
from jinja2 import FileSystemLoader, Environment
from optparse import OptionParser
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, TextIO # <- TextIO is for type - file
from packaging import version
from pathlib import Path
from loguru import logger
import re
import json


class CreateEndpoint():
    @staticmethod
    def create_endpoint_file(endpoint_metadata: Dict, template_file: str) -> str:
        content = None
        try:
            if template_file:
                logger.info(f"Found template file - {template_file}")
                environment = Environment(loader=FileSystemLoader("."))
                template = environment.get_template(template_file)
                content = template.render(endpoint=endpoint_metadata)
        except Exception as err:
            logger.error(f"Unable to render template, due to {err}")
        return content


class FunctionParamType(Enum):
    path = "args"
    query = "params"
    request_body = "json"


class UnsupportedOpenAPISpecVersion(Exception):
    """Custom Exception to handle unsupported OpenAPI spec versions"""
    def __init__(self, unsupported_spec_version: str) -> None:
        self.message = f"Un supported spec version - {unsupported_spec_version}. This script only supports OpenAPI spec v3.x"
        super().__init__(self.message)


@dataclass
class ParsedSpec():
    spec_file: TextIO
    version: str = field(init=False, repr=False)
    spec: specification.Specification = field(init=False, repr=False)
    paths: list[specification.Path] = field(init=False, repr=False)

    def __post_init__(self):
        self.spec = parse(self.spec_file)
        self.version = self.spec.version
        if version.parse(self.version) < version.parse('3.0'):
            raise UnsupportedOpenAPISpecVersion(self.version)
        logger.info(f"The version is {self.version}")
        logger.info(f"Parsing spec - {self.spec_file}")
        self.paths = self.spec.paths
        # parameters can be in two places:
        # 1. path.parameter
        # 2. path.operation.parameter
        # move all parameters to #2
        for path in self.paths:
            if hasattr(path, 'parameters'):
                for operation in path.operations:
                    if not operation.parameters:
                        operation.parameters = path.parameters


class EndpointModuleCreator(ParsedSpec):
    def __init__(self, spec_file):
        super().__init__(spec_file)

    def generate_dict_from_spec(self) -> dict:
        dict_from_spec = {}
        logger.info(f"Generating dictionary from OpenAPI spec")
        for path in self.paths:
            try:
                # group endpoints together based on the base endpoint
                # group /users & /users/add together
                # this is useful to add all similar endpoints in one file
                path_name = path.url
                logger.info(f"Parsing path - {path_name}")
                # if the endpoint is only /
                # make it /home
                # this is going to be a problem when there is /home
                if path_name == "/":
                    endpoint_split = ["home"]
                else:
                    endpoint_split = path_name.split("/")
                    endpoint_split = [ text for text in endpoint_split if text ]
                common_base_endpoint = endpoint_split[0]
                if dict_from_spec.get(common_base_endpoint):
                    dict_from_spec[common_base_endpoint]['endpoints'].append(path_name)
                else:
                    dict_from_spec[common_base_endpoint] = {'endpoints': [path_name]}

                # create filename module name for an endpoint group
                endpoints_in_a_file = [ endpoint.capitalize() for endpoint in re.split("-|_", common_base_endpoint) ]
                dict_from_spec[common_base_endpoint]['module_name'] = "_".join(endpoints_in_a_file) + "_" + "Endpoint"
                dict_from_spec[common_base_endpoint]['class_name'] = "".join(endpoints_in_a_file) + "Endpoint"
                dict_from_spec[common_base_endpoint]['url_method_name'] = common_base_endpoint.replace('-', '_') + "_" + "url"

                # create functions for every operation - http methods
                # identify the parameters for the functions
                for operation in path.operations:
                    function_details = {}
                    function_parameters = []
                    function_parameters.append({'name':'self', 'param_expression':'args'})
                    updated_endpoint_split = []
                    request_function_param = ''
                    parameter_string = 'self'
                    http_method = operation.method.name.lower()
                    for endpoint in endpoint_split:
                        endpoint = endpoint.replace("-","_")
                        if "{" in endpoint:
                            endpoint = re.sub("{|}", "", endpoint)
                            endpoint = "by_" + endpoint
                        updated_endpoint_split.append(endpoint)
                    name = http_method + "_" + "_".join(updated_endpoint_split)
                    function_details['name'] = name
                    function_details['endpoint'] = path_name
                    function_details['http_method'] = http_method
                    for param in operation.parameters:
                        param_dict = {}
                        if param.location.name.lower() == "path":
                            param_dict['name'] = param.name
                            param_dict['param_expression'] = FunctionParamType.path.value
                            param_dict['data_type'] = param.schema.type.name.lower()
                            parameter_string += ', ' + param.name
                        elif param.location.name.lower() == "query":
                            param_dict['param_expression'] = FunctionParamType.query.value
                            param_dict['name'] = param.name
                            param_dict['data_type'] = param.schema.type.name.lower()
                            if 'params' not in parameter_string:
                                parameter_string += ', ' + 'params'
                            if 'params' not in request_function_param:
                                request_function_param += ', ' + "params=params" 
                        function_parameters.append(param_dict)
                    if operation.request_body is not None:
                        for content in operation.request_body.content:
                            for property in content.schema.properties:
                                if hasattr(property.schema, 'properties'):
                                    for schema_prop in property.schema.properties:
                                        param_dict = {}
                                        param_dict['param_expression'] = FunctionParamType.request_body.value
                                        param_dict['name'] = schema_prop.name
                                        param_dict['data_type'] = schema_prop.schema.type.name.lower()
                                        function_parameters.append(param_dict)
                                else:
                                    param_dict = {}
                                    param_dict['param_expression'] = FunctionParamType.request_body.value
                                    param_dict['name'] = property.name
                                    param_dict['data_type'] = property.schema.type.name.lower()
                                    function_parameters.append(param_dict)
                                if 'json' not in request_function_param:
                                    request_function_param += ', '+ 'json=json'
                                if 'json' not in parameter_string:
                                    parameter_string += ', ' + 'json'
                    function_details['parameters'] = function_parameters

                    # Add headers to function param string
                    # auth should be handled in headers
                    request_function_param += ", " + "headers=headers"
                    parameter_string += ", " + "headers"
                    function_details['request_function_param'] = request_function_param
                    function_details['parameter_string'] = parameter_string
                    if dict_from_spec[common_base_endpoint].get('functions'):
                        dict_from_spec[common_base_endpoint]['functions'].append(function_details)
                    else:
                        dict_from_spec[common_base_endpoint]['functions'] = [function_details]
                    logger.info(f"Completed parsing path {path_name} & generated a dict from the path spec")
            except Exception as err:
                logger.warning(f"Unable to Parse Path - {path}, due to {err}")
                continue

        return dict_from_spec
 

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--spec",
                      dest="spec",
                      help="Location to the OpenAPI spec file")
    parser.add_option("--verbose",
                      dest="verbose",
                      action="store_true",
                      default=False,
                      help="Pass the verbose flag to print generated dict and content")
    parser.add_option("--create-endpoints",
                      dest="create_endpoints",
                      default=False,
                      action="store_true",
                      help="Create endpoint file if this option is passed")
    parser.add_option("--endpoints-location-full-path",
                      dest="endpoint_location",
                      default=None,
                      help="Directory to store the generated endpoints file")
    parser.add_option("--endpoints-template",
                      dest="endpoint_template",
                      help="Template file path")

    (options, args) = parser.parse_args()
    if options.spec:
        endpoint_module = EndpointModuleCreator(options.spec)
        metadata_dict = endpoint_module.generate_dict_from_spec()
        for endpoint, _ in metadata_dict.items():
            if options.create_endpoints:
                endpoint_location = options.endpoint_location
                endpoint_template = options.endpoint_template
                if not endpoint_template or not Path(endpoint_template).is_file:
                    logger.error(f"No template location passed or invalid template file")
                    endpoint_template = None
                if endpoint_location:
                    if Path(endpoint_location).is_dir():
                        endpoint_filename = Path(endpoint_location).joinpath(metadata_dict[endpoint]['module_name'] + '.py')
                else:
                    endpoint_filename = metadata_dict[endpoint]['module_name']+ '.py'
                if endpoint_filename and endpoint_template:
                    logger.info(f"The resultant Endpoint filename will be - {endpoint_filename}")
                    content = CreateEndpoint.create_endpoint_file(metadata_dict[endpoint], endpoint_template)
                    with open(endpoint_filename, 'w') as endpoint_file:
                        endpoint_file.write(content)
                        logger.info(f"Endpoint content render complete and saved the endpoint as file - {endpoint_filename}")
        if options.verbose:
            print(json.dumps(metadata_dict, indent=4))
            if options.create_endpoints:
                print(content)
    else:
        parser.print_help()