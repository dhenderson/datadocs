# Datadocs

Datadocs is static documentation for your datasets. I developed Datadocs to organize the vast number of datasets and fields we maintain at the [Family Independence Initiative][fii] (FII). Datadocs is fully searchable and great for internal use as well as sharing with external partners (we use it for both purposes at FII). 

Some key features of datadocs:

- Fully searchable static documentation that can be hosted anywhere, including off Dropbox or S3.
- Logically categorize fields, making it easier to quickly understand what a field a dataset contains.
- Designate which fields are private or protected, especially useful when sharing with external partners.
- Designate which fields are raw versus which have undergone some transformation. It's common to create new variables based on the raw data one has, keeping track of this makes for better, cleaner analysis.

You can view an example of datadocs with some dummy data on my personal site at [fullcontactphilanthropy/datadocs][example]. Datadocs is written for and tested in Python 3.4.

# Getting started

Your documentation goes in the `/docs` folder. You should delete the contents of the included example data and do the following:

1. **Add your data as csv files** - Datadocs requires each dataset to be a comma delimited `csv` file. Drop each of your `csv` files in the `/docs` folder and remove the "example.csv" file.
2. **Write yaml files for each csv** - Each `csv` file needs a `yaml` file of the same name. For example, if your dataset is `my_dataset.csv`, then Datadocs requires you to include a file named `my_dataset.yaml`. I recommend copying the `example.yaml` file and using that as a base template. How to write your `yaml` files is discussed in more detail in the following section on "Documenting and registering your data".
3. **[Optional] Include markdown files** - If you want, you can include markdown files with additional detail about your datasets. Like the `yaml` files, include a similarly named `md` file to provide additional documentation for a dataset. For example, add a `my_dataset.md` to render markdown content before the data documentation for your `my_dataset.csv` file.
4. **[Optional] Include an index.md file** - If you want to provide additional documentation on the index page of your documentation, you can include an `index.md` file. The `index.md` file is useful for giving a high level view of your data before a reader dives into the datasets.
5. **Register your datasets** - Before making your documentation, you need to register each dataset in the `datadocs.yaml` file. For example, to add the `my_dataset.csv` and its `yaml` and `md` files, simply add `my_dataset` to the list of datasets in the `datadocs.yaml` file.
6. **Make your documentation** - From the root directory execute `makedocs.py` with Python 3. Your static documentation will be built in the `/site` folder.

# Documenting and registering your data

This section provides more detail on how to document and register your data in datadocs.

## Documenting your data

Each dataset `yaml` files has the following structure:

```yaml
title: "Some title"
description: "Some description"
categories:
  - title: "Some category title"
    description: "Some category description"
    fields:
      - name: "Some field name as found in the .csv file"
        description: "Some description for this field"
```

Each field can also have have optional attributes as defined below.

### Type

The `type` attribute indicates a field's datatype. This field is optional as Datadocs attempts to guess a field's datatype based on the data provided in your `csv` file. If you want to make sure the documentation produces the correct datatype, or you want to override Datadocs's guess, you can do so with `type`.

Usage:

```yaml
fields:
  - name: "Some field name as found in the .csv file"
      description: "Some description for this field"
      type: "Date"
```

While you can provide any string for `type`, Datadocs expects one of the following:

- Boolean
- Categorical
- Date
- JSON
- Numeric
- Text
- Yaml

### Private

The `private` attribute indicates if a field is private or not. It is sometimes useful to document a field in a dataset and to share that you *have* a particular field, but that the field is somehow protected or private. A good example might be a Social Security number.

Usage:

```yaml
fields:
  - name: "Some field name as found in the .csv file"
    description: "Some description for this field"
    private: false
```

### Transformed

The `transformed` attribute indicates if a field underwent some form of transformation. For example, if we have household size and the number of people in a household as raw data and we calculate the household's federal poverty line, the new variable would be considered transformed.

Usage:

```yaml
fields:
  - name: "Some field name as found in the .csv file"
    description: "Some description for this field"
    transformed: false
```

## Registering your data

Your datasets are registered in `/docs/datadocs.yaml`. If you had the following tow datasets:

- my_dataset.csv
- some_other_dataset.csv

Your `datadocs.yaml` file might look like:

```yaml
title: "My data documentation"
show_uncategorized: false
show_percent_answered: false
show_private: true
datasets:
  - name: "my_dataset"
  - name: "some_other_dataset"
```

Note the file above also includes some metadata and settings, defined below:

**title** - Title for your documentation.
**show_uncategorized** - Whether to show fields you have not provided documentation for. Setting this attribute to `true` can be useful for determining which fields have not been documented yet.
**show_percent_answered** - Whether to show the percent of fields that are not null. For example, if you have ten observations for a field with three nulls, setting `show_percent_answered` to `true` would indicate that 70% of observations are not null in your documentation for that field.
**show_private** - Whether to include fields set to private when building the documentation. Toggling this attribute can be useful if you are sharing external documentation and you want to have certain fields documented, but you don't want others to know the field exists at all.

# Building your documentation

Build your documentation by navigating to the root `datadocs` folder and typing the following at your command line:

```bash
$ python3 makedocs.py
```

# Dependencies

A complete list of dependencies and version numbers are listed in the `requirements.txt` file in the root directory. Key dependencies are:

- python 3
- pandas
- Markdown
- Jinja2
- PyYaml

[fii]: http://fii.org
[example]: http://fullcontactphilanthropy.com/datadocs/