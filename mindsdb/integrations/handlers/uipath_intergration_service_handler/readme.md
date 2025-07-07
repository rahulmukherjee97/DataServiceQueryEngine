# Build your own Uipath AI agent

```
# Should be able to create a uipath database
CREATE DATABASE uipath_integration_service_datasource 
With 
    ENGINE = 'uipath_integration_service',
    PARAMETERS = {
       'api_base': Base url for uipath platfrom services,
       'token': Bearer token for uipath services,
       'organization': organization name for uipath access,
       'tenant': Tenant name for which you want access to the data ,
       'connection_id': Connector Id for integration service
       'connection_type': Connector Type in integration service (stripe/sap_c4c)
    };
```

This creates a database called `uipath_integration_service`. This database ships with a table called tweets that we can use to search for tweets as well as to write tweets.
