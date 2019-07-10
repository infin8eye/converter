#!/usr/bin/env python3
"""
Convert the format of input file to output file.

It infers the input and output file types from their extension:
  py, csv, json

example: convert.py --in input.csv --out output.json
"""
import os
import io
import argparse
import ast
import csv
import json


class BaseConverter:
    @staticmethod
    def deserialise(s):
        """Deserialise string into a dict"""
        return {}

    @staticmethod
    def serialise(d):
        """Serialise dict into a string"""
        return ""


class PyConverter(BaseConverter):
    @staticmethod
    def deserialise(s):
        return ast.literal_eval(s)

    @staticmethod
    def serialise(d):
        return repr(d)


class CsvConverter(BaseConverter):
    @staticmethod
    def deserialise(s):
        reader = csv.DictReader(s.splitlines())
        return list(reader)

    @staticmethod
    def serialise(d):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=d[0].keys())
        writer.writeheader()
        writer.writerows(d)
        return output.getvalue()


class JsonConverter(BaseConverter):
    @staticmethod
    def deserialise(s):
        return json.loads(s)

    @staticmethod
    def serialise(d):
        return json.dumps(d)


# todo: implement yaml support
class YamlConverter(BaseConverter):
    @staticmethod
    def deserialise(s):
        raise NotImplemented

    @staticmethod
    def serialise(d):
        raise NotImplemented


class ConvertInput:
    """ Convert input file for serialisation or deserialisation."""
    def __init__(self):
        # mapping between file type extension and converter class
        self.converter_type_map = {
            ".py": PyConverter,
            ".csv": CsvConverter,
            ".json": JsonConverter
        }

    def get_supported_extensions(self, printout=False):
        ext_list = []
        for ext in self.converter_type_map:
            ext_list.append(ext)
        if printout:
            print("The following extensions are supported: {ext_list}")
        return ext_list

    def get_converter(self, filename):
        """ Raise error if the conversion type does not match those specified."""
        try:
            file_ext = os.path.splitext(filename)[1]
            return self.converter_type_map[file_ext]
        except KeyError:
            raise Exception(f"Unrecognised file type: {filename}")

    def do_conversion(self, input_file, output_file):
        """ Detect file types, if compatible, run conversion.
        Reads input file, writes output file, in the chosen format.
        Returns the converted data as a Python dict.
        """
        # get input deserialiser
        deserialise = self.get_converter(input_file).deserialise
        # get output serialiser
        serialise = self.get_converter(output_file).serialise
        # read input
        with open(input_file) as file:
            input_string = file.read()
        # deserialise input to Python dict
        data = deserialise(input_string)
        # serialise to output
        output_string = serialise(data)
        # save output
        with open(output_file, "w") as write_file:
            write_file.write(output_string)
        return data


def main(args):
    convert = ConvertInput()
    outputData = convert.do_conversion(args.input_file, args.output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take input file and serialise/deserialise to output file")
    parser.add_argument("--in", help="input filename", dest="input_file", type=str, required=True)
    parser.add_argument("--out", help="output filename", dest="output_file", type=str, required=True)
    parser.set_defaults(func=main)
    args = parser.parse_args()
    try:
        outputData = args.func(args)
        print(f"Converted {args.input_file} to {args.output_file}")
    except Exception as e:
        print(f"Failed to convert {args.input_file} to {args.output_file}: {e}")
