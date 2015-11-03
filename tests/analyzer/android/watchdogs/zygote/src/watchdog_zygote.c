//#include "watchdog_zygote.h"

#include <unistd.h>
#include <stdio.h>
#include <string.h>
//#include <sys/types.h>
//#include <android/log.h>
//#include <utils/log.h>

#define LOG_TAG "Zygote watchdog"
#define RESULT_PATH "/data/local/tmp/strace.txt"

/*
watchAndStraceZygote: find zygote process and traces its system calls
returns: void
*/

struct process {
    int pid;
    char *name;
    int ppid;

};

typedef struct process MONITORED_PROCESSES;

void strace(int pid, char *outputFile) 
{
    char straceCommand[100];
    snprintf(straceCommand, 100, "su -c \"strace -p %d -o %s\" &", pid, outputFile);
    if(!fork()){
        system(straceCommand);
    }
}


/*
getProcName: gets the process name from /proc/<pid>/status
returns: char* process name
*/
char* getProcName(int pid) 
{
    char path[40], line[100], *p;
    FILE* statusf;

    snprintf(path, 40, "/proc/%d/status", pid);
    printf("opening proc %s\n", path);
    statusf = fopen(path, "r");
    //file not found
    if(!statusf){
        printf("not found file.\n");
        return NULL;
    }

    while(fgets(line, 100, statusf)) {
        if(strncmp(line, "Name:", 5) != 0)
            continue;
        // Ignore "State:" and whitespace
        p = line + 6;
        while(isspace(*p)) ++p;
        //printf("%6d %s", pid, p);

        break;
    }

    fclose(statusf);
    //printf("length of p is %d\n",strlen(p));
    printf("name is %s\n", p);

    return strdup(p);

}

void watchAndStraceZygote()
{
    system("rm -f %s", "/data/local/tmp/strace.txt");
    int pid = findZygote();

    char *straceResult = RESULT_PATH;
    strace(pid, straceResult);
    printf("zygote pid is %d\n", pid);
}

/*
monitorProcessForkIfExist: trace the system call of targeted process
returns: void
*/
void monitorProcessForkIfExist()
{
    const char resultPath[] = "/data/local/tmp/strace.txt";
    char path[40], line[100], *p;
    FILE* stracef;

    snprintf(path, 40, resultPath);
    stracef = fopen(path, "r");

    if(!stracef)
        return;

    while(fgets(line, 100, stracef)) {

        if (strncmp(line, "fork()", 6) != 0)
            continue;

        p = line + 6;
        while(isspace(*p)) ++p;
        //remove "= "
        ++p;
        ++p;
        printf("found process. PID %s\n", p);

        int isWhitelisted = checkAgainstWhitelist(p);   
        if (!isWhitelisted ) { //check if it's not whitelisted and not monitored at the moment
            char straceProcessResult[100];
            char *procName = getProcName(atoi(p));
            snprintf(straceProcessResult, 100, "/data/local/tmp/strace_%s", procName);
            strace(atoi(p), straceProcessResult);

            //other monitors will be started here.
        }
        //break;
    }
    fclose(stracef);
}

int checkAgainstWhitelist(char *pid)
{
    printf("checking against white list for %s...\n", pid);
    char *processName = getProcName(atoi(pid));

    if (processName == NULL){
        return 0;
    }

    //read from whitelist file and compare process name
    char path[40], line[100], *p;
    FILE* whitelistf;

    snprintf(path, 40, "/data/local/tmp/whitelist.txt");
    whitelistf = fopen(path, "r");

    if(!whitelistf){
        printf("whitelist file not found\n");
        return NULL;
    }

    while(fgets(line, 100, whitelistf)){
        if(strncmp(line, processName, strlen(processName)) != 0){
            continue;
        }else {
            return 1;
        }
    }

    //printf("checkAgainstWhitelist function, process name is %s\n", processName);
    return 0;

}

/*
strdup: Allocate memory for char* return
returns: char*
*/
char* strdup(const char* org)
{
    if(org == NULL) return NULL;

    char* newstr = malloc(strlen(org)+1);
    char* p;

    if(newstr == NULL) return NULL;

    p = newstr;

    while(*org) *p++ = *org++; /* copy the string. */
    return newstr;
}


int findZygote()
{
	int i = 1;
    char* output;
    for (i=1; i<1000; i++){
	    output = getProcName(i);
        printf("output is %s\n", output);
        char process[] = "zygote";

        if (output != NULL && strncmp(output, process, strlen(process)) == 0) {
            printf("found zygote\n");
            return i;
        }
        /*
		if (output == 1) {
			return i;
		}*/
	}
}




int main(int argc, char **argv)
{

	//LOGI("Zygote watchdog started");
    watchAndStraceZygote();
	while(1){
        printf("watching...\n");
		sleep(3);
		monitorProcessForkIfExist();
	}

	//findZygotePid();

}