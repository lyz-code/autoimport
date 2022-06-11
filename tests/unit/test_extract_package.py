"""Test the extraction of package objects."""

from autoimport.model import extract_package_objects


def test_extraction_returns_the_package_functions() -> None:
    """
    Given: A package with functions.
    When: extract package objects is called
    Then: All the functions are extracted
    """
    result = extract_package_objects("autoimport")

    desired_objects = {
        "fix_code": "from autoimport import fix_code",
        "fix_files": "from autoimport import fix_files",
        "extract_package_objects": (
            "from autoimport.model import extract_package_objects"
        ),
    }
    for object_name, object_import_string in desired_objects.items():
        assert result[object_name] == object_import_string


def test_extraction_returns_the_package_classes() -> None:
    """
    Given: A package with classes.
    When: extract package objects is called.
    Then: All the classes are extracted.
    """
    result = extract_package_objects("autoimport")

    desired_objects = {
        "SourceCode": "from autoimport.model import SourceCode",
    }
    for object_name, object_import_string in desired_objects.items():
        assert result[object_name] == object_import_string


def test_extraction_returns_the_package_dictionaries() -> None:
    """
    Given: A package with dictionaries.
    When: extract package objects is called.
    Then: All the dictionaries are extracted.
    """
    result = extract_package_objects("autoimport")

    desired_objects = {
        "common_statements": "from autoimport.model import common_statements",
    }
    for object_name, object_import_string in desired_objects.items():
        assert result[object_name] == object_import_string


def test_extraction_returns_empty_dict_if_package_is_not_importable() -> None:
    """
    Given: Autoimport can't import the package.
    When: the extract package objects is called.
    Then: An empty directory is returned
    """
    result = extract_package_objects("inexistent")

    assert not result
