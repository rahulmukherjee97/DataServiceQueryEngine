# ECS Commands for Shantanu Index

## 1. Create Index
```bash
curl 'https://alpha.uipath.com/07e28361-8ca4-4078-b585-d2365754994f/508b9064-94b0-4bf5-b3be-7e8a7dc2b991/ecs_/v2/indexes/create' \
  -X POST \
  -H 'Authorization: Bearer YOUR_BEARER_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "name": "shantanu",
    "description": "test",
    "dataSource": {
      "@odata.type": "#UiPath.Vdbs.Domain.Api.V20Models.StorageBucketDataSourceRequest",
      "folder": "Shared",
      "bucketName": "Shantanu",
      "fileNameGlob": "*",
      "directoryPath": "/"
    }
  }'
```

## 2. List All Indexes
```bash
curl 'https://alpha.uipath.com/07e28361-8ca4-4078-b585-d2365754994f/508b9064-94b0-4bf5-b3be-7e8a7dc2b991/ecs_/v2/indexes?$expand=*&$count=true&$top=10' \
  -H 'Authorization: Bearer YOUR_BEARER_TOKEN' \
  -H 'Content-Type: application/json'
```

## 3. Get Specific Index Details
```bash
curl 'https://alpha.uipath.com/07e28361-8ca4-4078-b585-d2365754994f/508b9064-94b0-4bf5-b3be-7e8a7dc2b991/ecs_/v2/indexes/shantanu' \
  -H 'Authorization: Bearer YOUR_BEARER_TOKEN' \
  -H 'Content-Type: application/json'
```

## 4. Delete Index
```bash
curl 'https://alpha.uipath.com/07e28361-8ca4-4078-b585-d2365754994f/508b9064-94b0-4bf5-b3be-7e8a7dc2b991/ecs_/v2/indexes/shantanu' \
  -X DELETE \
  -H 'Authorization: Bearer YOUR_BEARER_TOKEN' \
  -H 'Content-Type: application/json'
```

## 5. Search in Index
```bash
curl 'https://alpha.uipath.com/07e28361-8ca4-4078-b585-d2365754994f/508b9064-94b0-4bf5-b3be-7e8a7dc2b991/ecs_/v2/indexes/shantanu/search' \
  -X POST \
  -H 'Authorization: Bearer YOUR_BEARER_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "query": "your search query",
    "threshold": 0.7,
    "numberOfResults": 10
  }'
```

## 6. Ingest Data
```bash
curl 'https://alpha.uipath.com/07e28361-8ca4-4078-b585-d2365754994f/508b9064-94b0-4bf5-b3be-7e8a7dc2b991/ecs_/v2/indexes/shantanu/ingest' \
  -X POST \
  -H 'Authorization: Bearer YOUR_BEARER_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "content": "your content",
    "metadata": {
      "key": "value"
    }
  }'
```

## 7. Get Index Status
```bash
curl 'https://alpha.uipath.com/07e28361-8ca4-4078-b585-d2365754994f/508b9064-94b0-4bf5-b3be-7e8a7dc2b991/ecs_/v2/indexes/shantanu/status' \
  -H 'Authorization: Bearer YOUR_BEARER_TOKEN' \
  -H 'Content-Type: application/json'
```

## 8. Update Index
```bash
curl 'https://alpha.uipath.com/07e28361-8ca4-4078-b585-d2365754994f/508b9064-94b0-4bf5-b3be-7e8a7dc2b991/ecs_/v2/indexes/shantanu' \
  -X PATCH \
  -H 'Authorization: Bearer YOUR_BEARER_TOKEN' \
  -H 'Content-Type: application/json' \
  --data-raw '{
    "description": "updated description"
  }'
```

## Notes:
1. Replace `YOUR_BEARER_TOKEN` with your actual bearer token
2. The account ID is: `07e28361-8ca4-4078-b585-d2365754994f`
3. The tenant ID is: `508b9064-94b0-4bf5-b3be-7e8a7dc2b991`
4. All endpoints are prefixed with: `https://alpha.uipath.com/{account_id}/{tenant_id}/ecs_/v2/` 