# Functions to read the configuration file and read all the configurations
import os

__dir__ = os.path.dirname(__file__)
configuration_file = __dir__ + "/configuration.txt"


def create_configuration_file(_tol: float = 0.4,
                              _stol: float = 2.0,
                              _mtol: float = 0.4,
                              _mltol: float = 0.05):
    """ Create the configuration file
    This function create the configuration file when don't exist one

    Parameters:
    -----------
    _tol: float
        Tolerance for the creation of models

    Returns:
    --------
        None
    """
    _file = open(configuration_file, 'x')
    _text = []
    _config = {"Tolerance": _tol,
               "Smaller Tolerance": _tol/_stol,
               "Metric Tolerance": _mtol,
               "Metric lower Tolerance": round(_tol - _mltol, 2)
               # add more configuration here
               }
    for _key in _config:
        _text.append(_key + ':' + str(_config[_key]) + '\n')
    _file.writelines(_text)
    _file.close()


def change_configuration_file(_tol: float = None,
                              _stol: float = None,
                              _mtol: float = None,
                              _mltol: float = None):
    """ Change the configuration file
    This function read the configuration file and then change the configuration with the input values

    Parameters:
    -----------
    _tol: float
        Tolerance for the creation of models
    """
    if not os.path.isfile(configuration_file):
        create_configuration_file()
    _config = read_configuration_file()
    if _tol is not None:
        _tol = float(_tol) if type(_tol) is not float else _tol
        small_tol = (1/float(_config["Smaller Tolerance"])) * float(_config["Tolerance"])
        _config["Smaller Tolerance"] = _tol/small_tol
        _config["Metric Tolerance"] = _tol
        metric_lower_tol = abs(float(_config["Metric lower Tolerance"])-float(_config["Tolerance"]))
        _config["Metric lower Tolerance"] = _tol - metric_lower_tol
        _config["Tolerance"] = _tol

    _config["Smaller Tolerance"] = float(_stol) if _stol is not None else _config["Smaller Tolerance"]
    _config["Metric Tolerance"] = float(_mtol) if _mtol is not None else _config["Metric Tolerance"]
    _config["Metric lower Tolerance"] = float(_mltol) if _mltol is not None else _config["Metric lower Tolerance"]
    # add more configuration here
    _file = open(configuration_file, 'w')
    _text = []
    for _key in _config:
        _text.append(_key + ':' + str(_config[_key]) + '\n')
    _file.writelines(_text)
    _file.close()


def read_configuration_file():
    """ Read the configuration file
    This function read the configuration file and then change the configuration with the input values

    Returns
    -------
    _config: dict
        Dictionary with the configuration values
    """
    _file = open(configuration_file, 'r')
    _config = dict()
    for _line in _file.readlines():
        _line = _line.replace('\n', '') if '\n' in _line else _line
        _key, _value = _line.split(':')
        _config[_key] = _value
    _file.close()
    return _config


def default_configuration_file():
    """ Set the configuration file to default
    This function delete the previous configuration file and create new with default values
    """
    import os
    if os.path.isfile(configuration_file):
        os.remove(configuration_file)
    create_configuration_file()


if __name__ == "__main__":
    # create_configuration_file()
    # change_configuration_file(_tol=0.1)
    default_configuration_file()
