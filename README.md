# Datadocs

Datadocs automatically creates simple documentation for a set of datasets stored in `.csv` files. Organize your `.csv` files in folders in the `/data` directory, then run `makedocs.py` to generate static file documentation you can view in a browser. You can view a live version of documentation built using a test dataset at [fullcontactphilanthropy.com/datadocs](http://fullcontactphilanthropy.com/datadocs/). You can view the same sample locally by cloning this repository and opening the `index.html` file in `/docs`.

For each dataset, the number of rows and columns are calculated and presented, and each dataset variables are searchable with  a datatype and percent of observations with non-missing answers.

## Usage

Store your `.csv` files in subdirectories in the `/data` directory, replacing `/data/test` with your own folder(s) and `.csv` files.

To generate documentation, run:

```shell
$ python makedocs.py
```

Documentation will be generated in the `/docs` folder. Every time `makedocs.py` is run, all contents of `/docs` are purged and recreated.

## Dependencies

Datadocs is written in Python 3 and has the following dependencies:

* pandas
* jinja2
