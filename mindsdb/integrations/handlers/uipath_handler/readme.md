# Build your own Uipath AI agent

```
# Should be able to create a uipath database
CREATE DATABASE uipath_datasource 
With 
    ENGINE = 'uipath',
    PARAMETERS = {
       'api_base': Base url for uipath platfrom services,
       'token': Bearer token for uipath services,
       'organization': organization name for uipath access,
       'tenant': Tenant name for which you want access to the data ,
       'service_name': Name of the service where you want data to be fetched,
    };
```

This creates a database called `uipath_datasource`. This database ships with a table called tweets that we can use to search for tweets as well as to write tweets.
