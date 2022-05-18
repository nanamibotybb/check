#include <stdio.h>
#include <string.h>
#include "cJSON.h"

cJSON *parse_json(char *fn)
{
        FILE *fp;
        char buf[40 * 1024];
        fp = fopen(fn, "r"); /* json */
        fread(buf, 1, sizeof buf, fp);
        fclose(fp);
        return cJSON_Parse(buf);
}

char *get_uname(char *fn)
{
        char *s;
        for (s = fn; *s != '/'; ++s);
        return ++s;
}

int main(int argc, char *argv[])
{
        cJSON *json, *j, *s;
        char *uname;

        if (argc != 2)
                return 1;

#if 0
        for user in result["data"]["result"]:
            if user["uname"] == name:
                return user["mid"]
#endif
        j = json = parse_json(argv[1]);
        j = cJSON_GetObjectItem(j, "data");
        j = cJSON_GetObjectItem(j, "result");
        uname = get_uname(argv[1]);

        cJSON_ArrayForEach(s, j)
        {
                cJSON *n = cJSON_GetObjectItem(s, "uname");
                if (0 != strcmp(uname, n->valuestring))
                        continue;
                
                n = cJSON_GetObjectItem(s, "mid");
                printf("%d", n->valueint);
                break;
        }

        return 0;
}
