import pytest
from streaming_json_parser import StreamingJsonParser

def test_complete_json():
    parser = StreamingJsonParser()
    parser.consume('{"foo": "bar"}')
    print(parser.get())
    assert parser.get() == {"foo": "bar"}

def test_chunked_input():
    parser = StreamingJsonParser()
    parser.consume('{"foo":')
    parser.consume('"bar"}')
    print(parser.get())
    assert parser.get() == {"foo": "bar"}

def test_bad_chunk():
    parser = StreamingJsonParser()
    parser.consume('{"foo":')
    print(parser.get())
    assert parser.get() == {}

def test_partial_string_value():
    parser = StreamingJsonParser()
    parser.consume('{"foo": "bar')
    print(parser.get())
    assert parser.get() == {"foo": "bar"}

def test_nested_object():
    parser = StreamingJsonParser()
    parser.consume('{"outer": {"inner": "value"}')
    print(parser.get())
    parser.consume('}')
    print(parser.get())
    assert parser.get() == {"outer": {"inner": "value"}}

def test_whitespace_handling():
    parser = StreamingJsonParser()
    parser.consume('{ "key" : "value" }')
    print(parser.get())
    assert parser.get() == {"key": "value"}

def test_incomplete_key():
    parser = StreamingJsonParser()
    parser.consume('{"incomplete')
    print(parser.get())
    assert parser.get() == {}

def test_multiple_key_value_pairs():
    parser = StreamingJsonParser()
    parser.consume('{"k1": "v1", "k2": "v2"}')
    print(parser.get())
    assert parser.get() == {"k1": "v1", "k2": "v2"}

def test_empty_object():
    parser = StreamingJsonParser()
    parser.consume('{}')
    print(parser.get())
    assert parser.get() == {}

def test_partial_nested_object():
    parser = StreamingJsonParser()
    parser.consume('{"outer": {')
    print(parser.get())
    parser.consume('"inner": "val')
    print(parser.get())
    assert parser.get() == {"outer": {"inner": "val"}}

def test_hello_worl():
    parser = StreamingJsonParser()
    parser.consume('{"test": "hello", "worl')
    print(parser.get())
    assert parser.get() == {"test": "hello"}

def test_switz():
    parser = StreamingJsonParser()
    parser.consume('{"test": "hello", "country": "Switzerl')
    print(parser.get())
    assert parser.get() == {"test": "hello", "country": "Switzerl"}

def test_partial_key():
    parser = StreamingJsonParser()
    parser.consume('{ "ke')
    print(parser.get())
    assert parser.get() == {}
    parser.consume('y" : "value" }')
    print(parser.get())
    assert parser.get() == {"key":"value"}

def test_array_support():
    parser = StreamingJsonParser()
    parser.consume('{"data": [12, -3.5e2, "partial')
    assert parser.get() == {"data": [12, -350.0, "partial"]}
    parser.consume('", {"nested": 1}]}')
    assert parser.get() == {"data": [12, -350.0, "partial", {"nested": 1}]}

def test_partial_number():
    parser = StreamingJsonParser()
    parser.consume('{"temp": 36.')
    assert parser.get() == {}
    parser.consume('5}')
    assert parser.get() == {"temp": 36.5}