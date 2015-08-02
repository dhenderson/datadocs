import pandas as pd
import os, shutil
from jinja2 import Environment, PackageLoader

class DataFolder():
    """
    The data folder holds one or more datasets. The Data folder represents a
    physical folder anywhere in the /data directory.
    """

    def __init__(self, name):
        self.name = name
        self.datasets = [] # datasets directly under this data folder

class Dataset():
    """
    A dataset is a csv file that is either in the root /data directory or housed in
    a DataFolder anywhere in /data.
    """
    def __init__(self, name, pathToDataset, dataFolder):
        self.name = name
        self.pathToDataset = pathToDataset
        self.columns = []
        self.dataFolder = dataFolder

        # dimensions
        self.numberOfColumns = None
        self.numberOfRows = None

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
        df = pd.read_csv(self.pathToDataset, sep=',', header=0, encoding='ISO-8859-1', index_col=0)

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

            # set the properties and add the column to the dataset
            column  = Column(columnName, dataType, percentNotNA)
            print("%s - %s is %s" % (self.name, columnName, dataType))
            self.columns.append(column)

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
    def __init__(self, name, dataType, percentNotNA):
        self.name = name
        self.dataType = dataType
        self.percentNotNA = percentNotNA

if __name__ == "__main__":

    # remove the /docs dir if it exists
    if os.path.exists("docs"):
        shutil.rmtree('docs')
    # if docs doesn't exist, which it shouldn't, make it again
    if not os.path.exists('docs'):
        os.makedirs('docs')

    """
    Run through the /data folder making DataFolder and
    Dataset objects as needed.
    """
    dataFolders = []
    ignoredNames = [".DS_Store"]
    for folderName in os.listdir("data"):

        # make sure this is not a osx folder
        if folderName not in ignoredNames:
            # make a new Data folderName
            dataFolder = DataFolder(folderName)

            # add this datafolder name to the /docs/ directory
            if not os.path.exists('docs/%s' % dataFolder.name):
                os.makedirs('docs/%s' % dataFolder.name)

            for datasetName in os.listdir("data/" + folderName):
                if datasetName not in ignoredNames:

                    # construct the path to the dataset
                    pathToDataset = "data/%s/%s" % (folderName, datasetName)
                    # create the dataaset
                    dataset = Dataset(datasetName, pathToDataset, dataFolder)
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
    file = open('docs/index.html', 'w')
    file.write(template.render(dataFolders=dataFolders, static="static", home="index.html"))

    for dataFolder in dataFolders:
        # render data folder template
        template = env.get_template('datafolder.html')
        file = open('docs/%s/index.html' % dataFolder.name, 'w')
        file.write(template.render(dataFolder=dataFolder, static="../static", home="../index.html"))

        for dataset in dataFolder.datasets:
            # render data set template
            template = env.get_template('dataset.html')
            file = open('docs/%s/%s' % (dataFolder.name, dataset.getHtmlName()), 'w')
            file.write(template.render(dataset=dataset, static="../static", home="../index.html"))

    # copy static folder (css and images)
    shutil.copytree("static", "docs/static")
