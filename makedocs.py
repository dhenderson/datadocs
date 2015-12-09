import pandas as pd
import os, shutil
from jinja2 import Environment, PackageLoader
import yaml
import os.path

class DataFolder():
    """
    The data folder holds one or more datasets. The Data folder represents a
    physical folder anywhere in the /data directory.

    Args:
        name        String name of the folder, such as "test"
        datadocs    Dictionary contains data documentation for this folder as represented by a
                    user generated yaml file. Defaults to None assuming no datadocs.yaml file
                    is present.
    """

    def __init__(self, name, datadocs=None):
        self.name = name
        self.datasets = []
        self.datadocs = datadocs
        self.description = None
        self.title = None

        # get and set the title and description if they
        # were specified by the user
        if self.datadocs['description']:
            self.description = datadocs['description']
        if self.datadocs['title']:
            self.title = datadocs['title']

    def getNumberOfDatasets(self):
        """
        Counts and returns the number of datasets in this folder
        """
        return len(self.datasets)

class Dataset():
    """
    A dataset is a csv file that is either in the root /data directory or housed in
    a DataFolder anywhere in /data.

    Args:
        name            String full name of this dataset (such as "test.csv")
        pathToDataset   Relative path to the dataset
        dataFolder      DataFolder object this dataset is a member of
        title           String human readable title
        categories      List of dictionaries where each dictionary defines
                        a category that holds a number of columns from this
                        dataset
    """
    def __init__(self, name, pathToDataset, dataFolder, title=None):
        self.name = name
        self.pathToDataset = pathToDataset
        self.columns = []
        self.dataFolder = dataFolder

        # dimensions
        self.numberOfColumns = None
        self.numberOfRows = None

        self.title = title

        # set the columns
        self.setColumns()

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
        df = pd.read_csv(self.pathToDataset, sep=',', header=0, encoding='ISO-8859-1', index_col=None)

        # set dimensions
        self.numberOfRows = df.shape[0]
        self.numberOfColumns = df.shape[1]

        # get the names of the column headers
        columnNames = list(df.columns)

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

            """
            Get category and description
            """
            description = ""
            category = "Uncategorized"

            """
            Loop through each category and see if we can find the category
            that contains this column name. If we find it, set the category
            name and the description for this column
            """
            for category in categories:
                if columnName in category['columns']:
                    description = category['columns'][columnName]
                    if category['category']:
                        category = category['category']
                    # set the properties and add the column to the dataset
                    column  = Column(columnName, dataType, percentNotNA, description, category)
                    #print("%s - %s is %s" % (self.name, columnName, dataType))
                    self.columns.append(column)
                    break

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
    dataFolders = []
    ignoredNames = [".DS_Store", "datadocs.yaml"]

    # get all subdirectories in the directory
    dirs = [d for d in os.listdir('docs') if os.path.isdir(os.path.join('docs', d))]
    for folderName in dirs:

        # make sure this is not a osx folder
        if folderName not in ignoredNames:
            print(folderName)

            # check if there is a datadocs.yaml file in this directory
            datadocs = None
            try:
                datadocs = yaml.load(open("docs/" + folderName + "/datadocs.yaml", "r"))
            except:
                print("No datadocs.yaml file found in docs/%s" % folderName)

            # make a new Data folderName
            dataFolder = DataFolder(folderName, datadocs)

            # add this datafolder name to the /docs/ directory
            if not os.path.exists('site/%s' % dataFolder.name):
                os.makedirs('site/%s' % dataFolder.name)

            for datasetName in os.listdir("docs/" + folderName):
                if datasetName not in ignoredNames:

                    # construct the path to the dataset
                    pathToDataset = "docs/%s/%s" % (folderName, datasetName)
                    # create the dataaset
                    # TODO: handle nulls for title and categories
                    title = None
                    categories = None

                    if dataFolder.datadocs['datasets'][datasetName]['title']:
                        title = dataFolder.datadocs['datasets'][datasetName]['title']
                    if dataFolder.datadocs['datasets'][datasetName]['categories']:
                        categories = dataFolder.datadocs['datasets'][datasetName]['categories']

                    # create the dataset object
                    dataset = Dataset(datasetName, pathToDataset, dataFolder, title)

                    # add the dataset to the data folder
                    dataFolder.datasets.append(dataset)

            # add the data folder to the list of data folders
            dataFolders.append(dataFolder)

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
    # get the configuration file for the home page
    homeDatadocs = yaml.load(open("docs/datadocs.yaml", "r"))
    if homeDatadocs['title']:
        docTitle = homeDatadocs['title']
    if homeDatadocs['description']:
        docDescription = homeDatadocs['description']

    file.write(template.render(dataFolders=dataFolders, static="static", home="index.html", docTitle=docTitle, docDescription=docDescription))

    for dataFolder in dataFolders:
        # render data folder template
        template = env.get_template('datafolder.html')
        file = open('site/%s/index.html' % dataFolder.name, 'w')
        file.write(template.render(dataFolder=dataFolder, static="../static", home="../index.html", docTitle=docTitle))

        for dataset in dataFolder.datasets:
            # render data set template
            template = env.get_template('dataset.html')
            file = open('site/%s/%s' % (dataFolder.name, dataset.getHtmlName()), 'w')
            file.write(template.render(dataset=dataset, static="../static", home="../index.html", docTitle=docTitle))

    # copy static folder (css and images)
    shutil.copytree("static", "site/static")
