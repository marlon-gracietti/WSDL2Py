from zeep import Client
import os  # Make sure this line is added to import the 'os' module
from typing import Optional, List

# Type mapping from WSDL types to Python types
type_mapping = {
    'string': 'str',
    'decimal': 'float',
    'int': 'int',
    'boolean': 'bool',
    'long': 'int',
    'dateTime': 'datetime',
}

# To store generated classes, avoiding duplicates
generated_classes_set = set()
generated_classes_list = []  # Store classes in order

# Recursive function to extract minOccurs and generate the Python class for a given element
def generate_class(name, elements, original_tag, namespace):
    if name in generated_classes_set:
        return ""  # Avoid duplicate class generation
    
    generated_classes_set.add(name)  # Mark the class as generated
    
    # Use the original WSDL tag for the class, instead of the class name
    class_template = f"class {name}(SoapBody, tag='{original_tag}', ns=ns_par.abv, nsmap=ns_par.get_dict()):\n"
    
    nested_classes = []  # Store nested class definitions

    for element_name, element in elements:
        # Retrieve the minOccurs value for each element
        min_occurs = element.min_occurs if hasattr(element, 'min_occurs') else 1  # Default to 1 if not set
        is_optional = min_occurs == 0

        # Handle complex types and lists
        if hasattr(element.type, 'elements'):
            nested_class_name = f"{name}{element_name.capitalize()}"
            if nested_class_name not in generated_classes_set:
                nested_class = generate_class(nested_class_name, element.type.elements, element_name, namespace)
                if nested_class:  # Ensure only non-empty classes are added
                    nested_classes.append(nested_class)  # Store nested class for later
            class_template += f"    {element_name}_: Optional[{nested_class_name}] = element(tag='{element_name}', ns=ns_par.abv)\n"
        elif hasattr(element, 'max_occurs') and element.max_occurs != 1:
            # Handle list types
            item_type = element.type.name if hasattr(element.type, 'name') else 'str'
            class_template += f"    {element_name}_: Optional[List[{item_type}]] = element(tag='{element_name}', ns=ns_par.abv)\n"
        else:
            # Handle primitive types
            python_type = type_mapping.get(element.type.name, 'str')
            if is_optional:
                python_type = f"Optional[{python_type}]"
            class_template += f"    {element_name}_: {python_type} = element(tag='{element_name}', ns=ns_par.abv)\n"
    
    # Ensure nested classes are appended before the current class
    for nested_class in nested_classes:
        if nested_class:  # Make sure the nested class is not empty
            if nested_class not in generated_classes_list:
                generated_classes_list.append(nested_class)

    # Append the current class after its dependencies
    if class_template not in generated_classes_list:
        generated_classes_list.append(class_template)
    
    return class_template

# Function to extract and generate request/response classes from WSDL
def extract_and_generate_classes(wsdl_file_path, class_type='request'):
    if not os.path.exists(wsdl_file_path):
        print(f"Error: WSDL file not found at '{wsdl_file_path}'. Please check the file path.")
        return
    
    try:
        client = Client(wsdl_file_path)
    except Exception as e:
        print(f"Error: Unable to load the WSDL file. Details: {e}")
        return
    
    for service in client.wsdl.services.values():
        for port in service.ports.values():
            operations = port.binding._operations
            
            for operation in operations.values():
                if class_type == 'request':
                    input_elements = operation.input.body.type.elements
                    request_tag = operation.input.body.qname.localname
                    class_name = f"Request{operation.name.capitalize()}"
                else:
                    input_elements = operation.output.body.type.elements
                    request_tag = operation.output.body.qname.localname
                    class_name = f"Response{operation.name.capitalize()}"
                
                generate_class(class_name, input_elements, request_tag, namespace=None)
    
    # Print the classes in the correct order
    print(f"\nGenerated {class_type} classes in the correct order:\n")
    for class_def in generated_classes_list:  # No need to reverse, order is correct
        print(class_def)

# Path to the WSDL file
# wsdl_file_path = './ws.pedido.parametro.Service.wsdl'
wsdl_file_path = './sesuite.wsdl'

# Generate request and response classes
# extract_and_generate_classes(wsdl_file_path, class_type='request')  # For request
extract_and_generate_classes(wsdl_file_path, class_type='response')  # For response
