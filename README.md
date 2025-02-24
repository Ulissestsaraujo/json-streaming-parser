
# Streaming JSON Parser

A Python implementation of a streaming JSON parser designed to handle partial JSON data incrementally, particularly useful for processing streaming outputs from Large Language Models (LLMs).

## Features

- **Incremental Parsing**: Processes JSON data chunk-by-chunk  
- **Partial Value Handling**: Preserves incomplete string values and objects  
- **State Machine Architecture**: Clean state transitions with O(n) time complexity  
- **Support For**:  
  - Nested objects and arrays  
  - Strings, numbers (booleans, and null values to be added) 
  - Scientific notation in numbers  
- **Error Resilience**: Gracefully handles malformed fragments  

---

## Installation
No installation required - just include the `streaming_json_parser.py` file in your project.

**Requirements:** Python 3.6+

---

## Usage

### Basic Parsing
```python
from streaming_json_parser import StreamingJsonParser

parser = StreamingJsonParser()
parser.consume('{"name": "John", "age": 30}')
print(parser.get())  # {'name': 'John', 'age': 30}
```

---

### Chunked Input
```python
parser = StreamingJsonParser()
parser.consume('{"results": [12, {"status":')
parser.consume('"success", "data": "partial')
print(parser.get())  # {'results': [12, {'status': 'success', 'data': 'partial'}]}
```

---

### Nested Objects
```python
parser.consume('{"user": {"meta": {"tags": ["admin",')
parser.consume('"moderator"]}, "active": true}}')
print(parser.get())  # {'user': {'meta': {'tags': ['admin', 'moderator']}, 'active': True}}
```

---

## API Documentation

### **StreamingJsonParser Class**

#### Methods:
- `__init__()` : Initializes a new parser instance  
- `consume(buffer: str)` : Processes a string chunk of JSON data  
- `get() -> dict` : Returns the current parsed state  

#### Key Characteristics:
- Maintains parsing state between `consume()` calls  
- Immediately available partial results through `get()`  
- Automatically handles whitespace between tokens  

---

## Testing

Run the test suite with:
```bash
pytest test.py -v
```

**Test cases include:**  
- Deeply nested structures (up to 1000 levels)  
- Large inputs (1MB+ strings)  
- Mixed data types  
- Partial/incomplete JSON fragments  
- Whitespace variations  

---

## Assumptions

- No escape characters in strings  
- Unique keys within objects  
- No trailing commas in objects/arrays  
- Number precision matches Python's float type  

---

## Limitations

Doesn't support:  
- Unicode escape sequences  
- Hexadecimal numbers  
- Comments in JSON  
- Literals must be lowercase (true/false/null)  
- Maximum nesting depth limited by Python stack  

---

## License

**MIT License** - see [LICENSE](LICENSE) for details
