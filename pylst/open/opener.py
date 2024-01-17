# -*- coding: utf-8 -*-
"""
@author: Azad Rasul
"""
class Opener:
    @staticmethod
    def open(path, *args, **kwargs):
        # Simplified logic to open image
        try:
            file = open(path, 'rb')
            data = file.read()  # Read the file content
            print(f"Opened file: {path}")
            return file  # Return the file object
        except FileNotFoundError:
            print(f"File not found: {path}")
            return None  # Return None if the file is not found

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
