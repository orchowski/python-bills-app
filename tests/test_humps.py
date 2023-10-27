import humps


def test_camelize_dict():
    actual = {
        "date": "2022-02-14",
        "test_uuid": "9e3f4a89-9989-4190-89a0-f50ffa3826db",
    }
    expected = {
        "date": "2022-02-14",
        "testUuid": "9e3f4a89-9989-4190-89a0-f50ffa3826db",
    }

    result = humps.camelize(actual)

    assert expected == result