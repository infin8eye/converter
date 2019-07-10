"""
Unit tests for the converter library
"""

import pytest
import os
import collections

from converter.lib.convert import BaseConverter, PyConverter, CsvConverter, JsonConverter, ConvertInput

class TestConvert:


    TEST_DATA = [{'name': 'Joe Bloggs', 'age': '21', 'phone': '0412345678', 'address': '1 Somewhere Street, Sydney'},
                 {'name': 'Jim Bloggs', 'age': '42', 'phone': '0423456789', 'address': '1 Somewhere Street, Sydney'}]
    CONVERTER_MAP = {
        "file00.py": PyConverter,
        "file00.csv": CsvConverter,
        "file00.json": JsonConverter
    }

    @pytest.fixture
    def con_in(self):
        return ConvertInput()

    @pytest.fixture
    def dir_input(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        input_dir = "files_input"
        return os.path.join(this_dir, input_dir)

    @pytest.fixture
    def dir_output(self):
        this_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = "files_output"
        return os.path.join(this_dir, output_dir)

    def test_base_deser(self):
        deser = BaseConverter.deserialise(0)
        assert deser == {}


    def test_base_ser(self):
        ser = BaseConverter.serialise(0)
        assert ser == ""


    def test_py_deser(self, dir_input):
        data_path_input = os.path.join(dir_input, "file00.py")
        with open(data_path_input) as f:
            input_string = f.read()
            deser = PyConverter.deserialise(input_string)
            assert deser == self.TEST_DATA


    def test_py_ser(self):
        ser = PyConverter.serialise(self.TEST_DATA)
        assert ser == str(self.TEST_DATA)


    def test_csv_deser(self, dir_input):
        data_path_input = os.path.join(dir_input, "file00.csv")
        ordered_data = [collections.OrderedDict(x) for x in self.TEST_DATA]
        with open(data_path_input) as f:
            input_string = f.read()
            deser = CsvConverter.deserialise(input_string)
            assert deser == ordered_data


    def test_csv_ser(self):
        CSV_STRING_DATA = 'name,age,phone,address\r\n' \
                          'Joe Bloggs,21,0412345678,"1 Somewhere Street, Sydney"\r\n' \
                          'Jim Bloggs,42,0423456789,"1 Somewhere Street, Sydney"\r\n'
        ser = CsvConverter.serialise(self.TEST_DATA)
        assert ser == CSV_STRING_DATA


    def test_json_deser(self, dir_input):
        data_path_input = os.path.join(dir_input, "file00.json")
        with open(data_path_input) as f:
            input_string = f.read()
            deser = JsonConverter.deserialise(input_string)
            assert deser == self.TEST_DATA


    def test_json_ser(self):
        JSON_STRING_DATA = '[{"name": "Joe Bloggs", "age": "21", "phone": "0412345678", "address": "1 Somewhere Street, Sydney"}, {"name": "Jim Bloggs", "age": "42", "phone": "0423456789", "address": "1 Somewhere Street, Sydney"}]'
        ser = JsonConverter.serialise(self.TEST_DATA)
        assert ser == JSON_STRING_DATA


    def test_supported_extensions(self, con_in):
        ext_list_A = []
        for file in self.CONVERTER_MAP:
            ext_list_A.append(os.path.splitext(file)[1])
        ext_list_B = [x for x in con_in.get_supported_extensions()]
        matching_elements = set(ext_list_A).intersection(ext_list_B)
        assert len(ext_list_A) == len(matching_elements)


    def test_get_converter(self, con_in, dir_input):
        for file, converter_class in iter(self.CONVERTER_MAP.items()):
            data_path_input = os.path.join(dir_input, file)
            assert con_in.get_converter(data_path_input) == converter_class


    def test_do_conversion(self, con_in, dir_input, dir_output):
        for file in self.CONVERTER_MAP:
            data_path_input = os.path.join(dir_input, file)
            data_path_output = os.path.join(dir_output, file)
            con_in.do_conversion(data_path_input, data_path_output)
            with open(data_path_input) as file_A, open(data_path_output) as file_B:
                assert file_A.read() == file_B.read()

