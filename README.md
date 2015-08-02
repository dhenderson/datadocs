# Datadocs

Datadocs automatically creates simple documentation for a set of datasets stored in `.csv` files.

## Usage

Store your `.csv` files in subdirectories in the `/data` directory, replacing `/data/test` with your own folder(s) and `.csv` files. 

To generate documentation, run:

```
$ python makedocs.py
```

Documentation will be generated in the `/docs` folder. Every time `makedocs.py` is run, all contents of `/docs` are purged and recreated.

## Dependencies

Datadocs is written in Python 3 and has the following dependencies:

* pandas
* jinja2