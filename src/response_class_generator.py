from zeep import Client
from collections import defaultdict
import os

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

# Function to generate Python class for a given element and its type
def generate_class(name, elements):
    if name in generated_classes_set:
        return ""  # Avoid duplicate class generation
    
    generated_classes_set.add(name)  # Mark the class as generated
    class_template = f"class {name}(BodyContent, tag='{name}', ns=ns_ped.abv, nsmap=ns_ped.get_dict()):\n"
    
    for element_name, element_type in elements.items():
        # Handle complex types and lists
        if hasattr(element_type, 'elements'):
            nested_class_name = element_type.name or element_name
            nested_class = generate_class(nested_class_name, {el[0]: el[1].type for el in element_type.elements})
            class_template += f"    {element_name}: Optional[{nested_class_name}] = element(tag='{element_name}', ns=ns_ped.abv)\n"
            class_template += nested_class  # Append nested class
        elif hasattr(element_type, 'max_occurs') and element_type.max_occurs != 1:
            # Handle list types
            item_type = element_type.type.name if hasattr(element_type.type, 'name') else 'str'
            class_template += f"    {element_name}: Optional[list[{item_type}]] = element(tag='{element_name}', ns=ns_ped.abv)\n"
        else:
            # Handle primitive types
            python_type = type_mapping.get(element_type.name, 'Optional[str]')
            class_template += f"    {element_name}: Optional[{python_type}] = element(tag='{element_name}', ns=ns_ped.abv)\n"
    
    return class_template

# Function to extract and generate response classes from WSDL
def extract_and_generate_response_classes(wsdl_file_path):
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
                if operation.output is not None:
                    output_elements = {el[0]: el[1].type for el in operation.output.body.type.elements}
                    class_name = f"PResponse{operation.name}" if operation.name != "incluir" else "PResponsePedidoVendaXML"
                    response_class = generate_class(class_name, output_elements)
                    generated_classes.append(response_class)
    
    print("\nGenerated response classes:\n")
    for class_def in generated_classes:
        print(class_def)

# Path to the WSDL file (replace with your WSDL file path)
wsdl_file_path = 'ws.pedido.parametro.Service.wsdl'

# Generate response classes based on WSDL
extract_and_generate_response_classes(wsdl_file_path)
