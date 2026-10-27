
import importlib


def test_settings_module_imports():
    module = importlib.import_module("config.settings")
    assert module is not None
