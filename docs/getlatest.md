# getlatest.py

This module provides a function to get the latest OTA (Over-The-Air) update from Rabbit's services.

## Functions

### getLatestOTA()

Makes a GET request to the OTA URL and returns the response.

**Returns:**

- If the request is successful, it returns the response text parsed with `multiline.loads()`.
- If the request fails, it returns `False`.

**Return example (in JSON):**
```json
{
    "name": "production ota",
    "version": "rabbit_OS_v0.8.86_20240523151103",
    "info": "Information",
    "url": "https://s3.us-west-2.amazonaws.com/rabbit-ota.transactional.pub/ota-pkgs/rabbit_OS_v0.8.50_20240407162326_rabbit_OS_v0.8.86_20240523151103_ota.zip",
    "property_files": [
        {
            "filename": "payload_metadata.bin",
            "offset": 3122,
            "size": 1028435
        },
        {
            "filename": "payload.bin",
            "offset": 3122,
            "size": 56864257
        },
        {
            "filename": "payload_properties.txt",
            "offset": 56867437,
            "size": 155
        },
        {
            "filename": "apex_info.pb",
            "offset": 2741,
            "size": 0
        },
        {
            "filename": "care_map.pb",
            "offset": 2788,
            "size": 287
        },
        {
            "filename": "metadata",
            "offset": 69,
            "size": 860
        },
        {
            "filename": "metadata.pb",
            "offset": 997,
            "size": 1696
        }
    ]
}
```
**Note that only 'streaming / incremental ota' updates have property_files`**


## Environment Variables

- `OTA_URL`: The URL for the OTA updates.