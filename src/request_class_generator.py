from zeep import Client
from collections import defaultdict
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

# Recursive function to extract minOccurs and generate the Python class for a given element
def generate_class(name, elements, original_tag, namespace):
    if name in generated_classes_set:
        return ""  # Avoid duplicate class generation
    
    generated_classes_set.add(name)  # Mark the class as generated
    
    # Use the original WSDL tag for the class, instead of the class name
    class_template = f"class {name}(BodyContent, tag='{original_tag}', ns=ns_par.abv, nsmap=ns_par.get_dict()):\n"
    
    for element_name, element in elements:
        # Retrieve the minOccurs value for each element
        min_occurs = element.min_occurs if hasattr(element, 'min_occurs') else 1  # Default to 1 if not set
        is_optional = min_occurs == 0

        # Handle complex types and lists
        if hasattr(element.type, 'elements'):
            nested_class_name = f"{name}{element_name.capitalize()}"
            nested_class = generate_class(nested_class_name, element.type.elements, element_name, namespace)
            class_template += f"    {element_name}: Optional[{nested_class_name}] = element(tag='{element_name}', ns=ns_par.abv)\n"
            class_template += nested_class  # Append nested class
        elif hasattr(element, 'max_occurs') and element.max_occurs != 1:
            # Handle list types
            item_type = element.type.name if hasattr(element.type, 'name') else 'str'
            class_template += f"    {element_name}: Optional[List[{item_type}]] = element(tag='{element_name}', ns=ns_par.abv)\n"
        else:
            # Handle primitive types
            python_type = type_mapping.get(element.type.name, 'str')
            if is_optional:
                python_type = f"Optional[{python_type}]"
            class_template += f"    {element_name}: {python_type} = element(tag='{element_name}', ns=ns_par.abv)\n"
    
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
    
    generated_classes = []
    
    for service in client.wsdl.services.values():
        for port in service.ports.values():
            operations = port.binding._operations
            
            for operation in operations.values():
                if class_type == 'request':
                    input_elements = operation.input.body.type.elements
                    request_tag = operation.input.body.qname.localname
                    class_name = f"PRequest{operation.name.capitalize()}"
                else:
                    input_elements = operation.output.body.type.elements
                    request_tag = operation.output.body.qname.localname
                    class_name = f"PResponse{operation.name.capitalize()}"
                
                request_class = generate_class(class_name, input_elements, request_tag, namespace=None)
                generated_classes.append(request_class)
    
    print(f"\nGenerated {class_type} classes:\n")
    for class_def in generated_classes:
        print(class_def)

# Path to the WSDL file
wsdl_file_path = './ws.pedido.parametro.Service.wsdl'

# Generate request and response classes
extract_and_generate_classes(wsdl_file_path, class_type='request')  # For request
# extract_and_generate_classes(wsdl_file_path, class_type='response')  # For response
