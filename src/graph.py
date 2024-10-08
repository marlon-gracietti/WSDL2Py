import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import networkx as nx
import os

# Parse the WSDL file and extract relevant information
def parse_wsdl(wsdl_file):
    tree = ET.parse(wsdl_file)
    root = tree.getroot()
    
    ns = {
        'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
        'soap': 'http://schemas.xmlsoap.org/wsdl/soap/',
        'xsd': 'http://www.w3.org/2001/XMLSchema'
    }
    
    # Extract service, portType, and binding details
    services = {}
    for service in root.findall('wsdl:service', ns):
        service_name = service.attrib['name']
        services[service_name] = []
        
        # Get ports for this service
        for port in service.findall('wsdl:port', ns):
            binding_name = port.attrib['binding'].split(":")[-1]
            location = port.find('soap:address', ns).attrib['location']
            services[service_name].append((binding_name, location))
    
    operations = {}
    for port_type in root.findall('wsdl:portType', ns):
        port_type_name = port_type.attrib['name']
        operations[port_type_name] = []
        
        for operation in port_type.findall('wsdl:operation', ns):
            operation_name = operation.attrib['name']
            operations[port_type_name].append(operation_name)

    return services, operations

# Visualize the services and their operations
def visualize_infrastructure(services, operations, output_file):
    G = nx.DiGraph()
    
    # Add nodes for services and their bindings
    for service, bindings in services.items():
        G.add_node(service)
        for binding, location in bindings:
            binding_label = f"{binding}\n({location})"
            G.add_edge(service, binding_label)
    
    # Add nodes for operations
    for port_type, ops in operations.items():
        for op in ops:
            G.add_edge(port_type, op)
    
    # Draw the graph
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=10, font_weight='bold', arrows=True)
    plt.title("WSDL Service Infrastructure")
    
    # Save the figure to a file
    plt.savefig(output_file)
    plt.close()

# Main function to parse and visualize the WSDL file
def main():
    # wsdl_file = 'boNotificacaoPortalWSService.wsdl.xml'  # Replace with your WSDL file path
    wsdl_file = './examples/wsdl/ws.pedido.parametro.Service.wsdl.xml'  # Replace with your WSDL file path
    # wsdl_file = r'.\examples\wsdl\boNotificacaoPortalWSService.wsdl.xml'  # Replace with your WSDL file path

    
    # Define output directory and file
    output_dir = 'docs/img'
    os.makedirs(output_dir, exist_ok=True)  # Create folder if it doesn't exist
    output_file = os.path.join(output_dir, os.path.basename(wsdl_file).replace('.xml', '.png'))  # Save as .png with the same name as the input file
    
    # Parse the WSDL file to extract services and operations
    services, operations = parse_wsdl(wsdl_file)
    
    # Visualize the infrastructure and save the image
    visualize_infrastructure(services, operations, output_file)
    print(f"Image saved to {output_file}")

# Run the main function
if __name__ == "__main__":
    main()
