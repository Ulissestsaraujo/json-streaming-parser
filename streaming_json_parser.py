from io import StringIO
from enum import Enum, auto
import json


class State(Enum):
    INIT = auto()
    IN_OBJECT = auto()
    IN_KEY = auto()
    AFTER_KEY = auto()
    AFTER_COLON = auto()
    IN_STRING_VALUE = auto()
    AFTER_VALUE = auto()
    IN_ARRAY = auto()
    AFTER_ARRAY_VALUE = auto()
    IN_NUMBER = auto()
    DONE = auto()


class StreamingJsonParser:
    def __init__(self):
        self.reset()

    def reset(self):
        self.stack = []
        self.root = {}
        self.current_object = self.root
        self.state = State.INIT
        self.current_key = None
        self.partial_key = StringIO()
        self.number_buffer = []
        self.whitespace = {' ', '\n', '\t', '\r'}
        self._init_state_handlers()

    def _init_state_handlers(self):
        self.handlers = {
            State.INIT: self._handle_init,
            State.IN_OBJECT: self._handle_in_object,
            State.IN_KEY: self._handle_in_key,
            State.AFTER_KEY: self._handle_after_key,
            State.AFTER_COLON: self._handle_after_colon,
            State.IN_STRING_VALUE: self._handle_in_string_value,
            State.AFTER_VALUE: self._handle_after_value,
            State.IN_ARRAY: self._handle_in_array,
            State.AFTER_ARRAY_VALUE: self._handle_after_array_value,
            State.IN_NUMBER: self._handle_in_number,
        }

    def consume(self, buffer: str):
        for char in buffer:
            if self.state == State.DONE:
                break
            if char in self.whitespace:
                if self.state not in [State.IN_STRING_VALUE, State.IN_NUMBER]:
                    continue
            handler = self.handlers.get(self.state, lambda _: None)
            handler(char)

    # State handlers
    def _handle_init(self, char):
        if char == '{':
            self.state = State.IN_OBJECT

    def _handle_in_object(self, char):
        if char == '}':
            self._close_container()
        elif char == '"':
            self.partial_key = StringIO()
            self.state = State.IN_KEY
        elif char == '[':
            self._start_nested_container('array')

    def _handle_in_key(self, char):
        if char == '"':
            self.current_key = self.partial_key.getvalue()
            self.state = State.AFTER_KEY
        else:
            self.partial_key.write(char)

    def _handle_after_key(self, char):
        if char == ':':
            self.state = State.AFTER_COLON

    def _handle_after_colon(self, char):
        if char == '"':
            self._start_string_value()
        elif char == '{':
            self._start_nested_container('object')
        elif char == '[':
            self._start_nested_container('array')
        elif self._is_number_start(char):
            self._start_number(char)

    def _handle_in_string_value(self, char):
        if char == '"':
            self._finalize_string()
        else:
            if isinstance(self.current_object, dict):
                self.current_object[self.current_key].write(char)
            else:
                self.current_object[-1].write(char)

    def _handle_after_value(self, char):
        if char == ',':
            if isinstance(self.current_object, dict):
                self.state = State.IN_OBJECT
            else:
                self.state = State.IN_ARRAY
        elif char in ('}', ']'):
            self._close_container()

    def _handle_in_array(self, char):
        if char == ']':
            self._close_container()
        elif char == '"':
            self._start_string_value(array_context=True)
        elif char == '{':
            self._start_nested_container('object')
        elif char == '[':
            self._start_nested_container('array')
        elif self._is_number_start(char):
            self._start_number(char)
        elif char == ',':
            pass

    def _handle_after_array_value(self, char):
        if char == ',':
            self.state = State.IN_ARRAY
        elif char == ']':
            self._close_container()

    def _handle_in_number(self, char):
        if char in '0123456789.eE+-':
            self.number_buffer.append(char)
        else:
            self._finalize_number()
            self.handlers[self.state](char)

    # Helper methods
    def _start_nested_container(self, container_type):
        new_container = {} if container_type == 'object' else []
        if isinstance(self.current_object, dict):
            self.current_object[self.current_key] = new_container
        else:
            self.current_object.append(new_container)
        self.stack.append((self.current_object, self.current_key, container_type))
        self.current_object = new_container
        self.state = State.IN_OBJECT if container_type == 'object' else State.IN_ARRAY
        self.current_key = None

    def _start_string_value(self, array_context=False):
        buffer = StringIO()
        if array_context:
            self.current_object.append(buffer)
        else:
            self.current_object[self.current_key] = buffer
        self.state = State.IN_STRING_VALUE

    def _finalize_string(self):
        if isinstance(self.current_object, dict):
            self.current_object[self.current_key] = self.current_object[self.current_key].getvalue()
        else:
            self.current_object[-1] = self.current_object[-1].getvalue()
        self.state = State.AFTER_ARRAY_VALUE if isinstance(self.current_object, list) else State.AFTER_VALUE

    def _start_number(self, char):
        self.number_buffer = [char]
        self.state = State.IN_NUMBER

    def _finalize_number(self):
        try:
            num_str = ''.join(self.number_buffer)
            number = json.loads(num_str)
            if isinstance(self.current_object, list):
                self.current_object.append(number)
            else:
                self.current_object[self.current_key] = number
        except ValueError:
            pass
        self.number_buffer = []
        self.state = State.AFTER_ARRAY_VALUE if isinstance(self.current_object, list) else State.AFTER_VALUE

    def _close_container(self):
        if self.stack:
            prev_obj, prev_key, container_type = self.stack.pop()
            self.current_object = prev_obj
            if container_type == 'object':
                self.state = State.AFTER_VALUE
            else:
                self.state = State.AFTER_ARRAY_VALUE
        else:
            self.state = State.DONE

    def _is_number_start(self, char):
        return char in '-0123456789' or (char == '.' and self.number_buffer)

    def get(self):
        def convert(obj):
            if isinstance(obj, dict):
                return {k: convert(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert(v) for v in obj]
            elif isinstance(obj, StringIO):
                return obj.getvalue()
            return obj

        return convert(self.root)