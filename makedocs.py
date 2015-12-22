import pandas as pd
import os, shutil
from jinja2 import Environment, PackageLoader
import yaml
import os.path

class Dataset():
    """
    A dataset is a csv file that is either in the root /data directory or housed in
    a DataFolder anywhere in /data.

    Args:
        name                String full name of this dataset (such as "test.csv")
        pathToDataset       Relative path to the dataset
        dataFolder          DataFolder object this dataset is a member of
        title               String human readable title
        categories          List of dictionaries where each dictionary defines
                            a category that holds a number of columns from this
                            dataset
        showUncategorized   Boolean indicating whether uncategorized columns should be shown in the documentation or not.
    """
    def __init__(self, name, title=None, categories=None, showUncategorized=False):
        self.name = name
        self.columns = []
        #self.dataFolder = dataFolder

        # dimensions
        self.numberOfColumns = None
        self.numberOfRows = None

        self.showUncategorized = showUncategorized

        self.title = title

        # categories as defined in yaml
        self.categories = categories

        # set the columns and return a map of column names and list of columns
        self.columnsByCategory = self.setColumns()

    def setColumns(self):

        # the datatype map maps pandas data types to user friendly types
        dataTypeMap = {
            "object" : "Text",
            "int64" : "Numeric",
            "float64" : "Numeric",
            "bool" : "Boolean",
            "date" : "Date",
            "categorical" : "Categorical"
        }

        # read the data set as a csv and convert to a data frame
        df = pd.read_csv("docs/" + self.name, sep=',', header=0, encoding='ISO-8859-1', index_col=None)

        # set dimensions
        self.numberOfRows = df.shape[0]
        self.numberOfColumns = df.shape[1]

        # get the names of the column headers
        columnNames = list(df.columns)
        columnsByCategory = {}

        for columnName in columnNames:

            # percent not NA is 1 minus the percent NA
            percentNotNA = 1 - (pd.isnull(df[columnName]).sum()/len(df[columnName]))
            percentNotNA = round(percentNotNA*100)

            # set the data type
            dataType = dataTypeMap[str(df[columnName].dtype)]

            # look for special cases where we guess a different datatype
            if "date" in columnName.lower():
                dataType = dataTypeMap["date"]
            # check if a text datatype is actually categorical
            elif dataType == "Text":
                # if there are fewer than k unique answers, then guess it's categorical
                numberOfUniqueAnswers = len(df[columnName].value_counts())
                if numberOfUniqueAnswers < 20: # TODO: This is kind of a hack, might think of a better solution
                      dataType = dataTypeMap["categorical"]

            # track whether we categorized the column
            columnCategorized = False

            """
            Loop through each category and see if we can find the category
            that contains this column name. If we find it, set the category
            name and the description for this column
            """
            for category in self.categories:

                # make a new category object
                if category['category'] not in columnsByCategory:
                    columnsByCategory[category['category']] = []

                if columnName in category['columns']:
                    description = category['columns'][columnName]
                    if category['category']:
                        category = category['category']
                    # set the properties and add the column to the dataset
                    column  = Column(columnName, dataType, percentNotNA, description, category)
                    #print("%s - %s is %s" % (self.name, columnName, dataType))
                    self.columns.append(column)
                    columnsByCategory[category].append(column)
                    columnCategorized = True
                    break
            if not columnCategorized and self.showUncategorized == True:
                """
                this column is both uncategorized and the user wants us to
                show uncategorized columns, so lets add this column to a new group
                titled "uncategorized"
                """

                # make a new category object
                if "Uncategorized" not in columnsByCategory:
                    columnsByCategory["Uncategorized"] = []

                # set the properties and add the column to the dataset
                column  = Column(columnName, dataType, percentNotNA, description=None, category=category)
                #print("%s - %s is %s" % (self.name, columnName, dataType))
                self.columns.append("Uncategorized")
                columnsByCategory["Uncategorized"].append(column)

        return columnsByCategory

    def getHtmlName(self):
        """
        Returns a string takign the file name and turning it into a
        reasonable html file name that strips white space and .csv
        """
        htmlName = self.name.replace(' ', '_')
        htmlName = htmlName.replace('.csv', '')
        htmlName += '.html'
        return htmlName

class Column():
    """
    A column in a dataset.
    """
    def __init__(self, name, dataType, percentNotNA, description=None, category=None):
        self.name = name
        self.dataType = dataType
        self.percentNotNA = percentNotNA
        self.description = description
        self.category = category

if __name__ == "__main__":

    # remove the /docs dir if it exists
    if os.path.exists("site"):
        shutil.rmtree('site')
    # if docs doesn't exist, which it shouldn't, make it again
    if not os.path.exists('site'):
        os.makedirs('site')

    """
    Run through the /data folder making DataFolder and
    Dataset objects as needed.
    """
    #dataFolders = []
    ignoredNames = [".DS_Store", "datadocs.yaml"]

    # get all subdirectories in the directory
    dirs = [d for d in os.listdir('docs') if os.path.isdir(os.path.join('docs', d))]
    #for folderName in dirs:

    datadocs = yaml.load(open("docs/datadocs.yaml", "r"))
    showUncategorized = datadocs['show_uncategorized']

    # create a list of datasets
    datasets = []

    for datasetName in os.listdir("docs"):
        if datasetName not in ignoredNames:
            if datasetName in datadocs['datasets']:
                # construct the path to the dataset
                pathToDataset = "docs/%s/" % datasetName
                # create the dataaset
                # TODO: handle nulls for title and categories
                title = None
                categories = None

                if datadocs['datasets'][datasetName]['title']:
                    title = datadocs['datasets'][datasetName]['title']
                if datadocs['datasets'][datasetName]['categories']:
                    categories = datadocs['datasets'][datasetName]['categories']

                # create the dataset object
                dataset = Dataset(datasetName, title, categories, showUncategorized)

                # add the dataset to the data folder
                datasets.append(dataset)

    """
    Render templates
    """
    # jinja2 templating settings
    env = Environment(loader=PackageLoader('makedocs', 'templates'))

    # make index page
    template = env.get_template('home.html')
    file = open('site/index.html', 'w')

    # documentation properties
    docTitle = None
    docDescription = None
    showPercentAnswered = None
    # get the configuration file for the home page
    homeDatadocs = yaml.load(open("docs/datadocs.yaml", "r"))
    if homeDatadocs['title']:
        docTitle = homeDatadocs['title']
    if homeDatadocs['description']:
        docDescription = homeDatadocs['description']
    if homeDatadocs['show_percent_answered']:
        showPercentAnswered = homeDatadocs['show_percent_answered']

    file.write(template.render(datasets=datasets, static="static", home="index.html", docTitle=docTitle, docDescription=docDescription))

    for dataset in datasets:
        template = env.get_template('dataset.html')
        file = open('site/%s' % (dataset.getHtmlName()), 'w')
        file.write(template.render(dataset=dataset, static="static", home="index.html", docTitle=docTitle, showPercentAnswered=showPercentAnswered,
            showUncategorized=showUncategorized))

    # copy static folder (css and images)
    shutil.copytree("static", "site/static")
