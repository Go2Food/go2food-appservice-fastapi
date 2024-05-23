set arg1=%1
shift
pytest %arg1% -s -x -W ignore::DeprecationWarning