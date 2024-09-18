[![CodeQL](https://github.com/marlon-gracietti/WSDL2Py/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/marlon-gracietti/WSDL2Py/actions/workflows/github-code-scanning/codeql)

# WSDL2Py - SOAP Class Generator from WSDL

This project aims to automatically generate Python classes from WSDL files, simplifying the usage of SOAP services in Python applications.

## Requirements

Before running the script, you will need to install Python and the `zeep` library.

### Installing `zeep`

You can install the `zeep` library with the following command:

```bash
pip install zeep
```

## How to Use

1. **Place the WSDL file in the correct location**: Make sure the WSDL file path is correct in the script. For example:

```python
wsdl_file_path = './ws.pedido.parametro.Service.wsdl'
```

2. **Choose between generating request or response classes**:
   - To **generate request classes**, uncomment the corresponding line in the script:
     ```python
     # extract_and_generate_classes(wsdl_file_path, class_type='request')
     ```
   - To **generate response classes**, keep this line:
     ```python
     extract_and_generate_classes(wsdl_file_path, class_type='response')
     ```

3. **Run the script**: With the WSDL file ready and the class type selected, run the script in the terminal:

```bash
python generate_classes.py
```

4. **View the generated classes**: The generated classes will be displayed in the terminal, making it easy to integrate them into your project.

## Example Output

When running the script, the generated output will look like this:

```python
class PResponseBuscar(BodyContent, tag='buscarResponse', ns=ns_par.abv):
    buscarResult: Optional[Response] = element(tag='buscarResult', ns=ns_par.abv)
```
