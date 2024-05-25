import mysql.connector

database = mysql.connector.connect(
    #host = 'roundhouse.proxy.rlwy.net',
    host = 'localhost',
    #port='53639',
    user = 'root',
    #password = 'ViLFATxWZERwtqrgsOcxqjcCUIZqPfIb',
    password = '',
    #database = 'railway'
    database = 'med_system'
)
