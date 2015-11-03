#include "zygotew.h"

#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <android/log.h>

#define LOG_TAG "Zygote watchdog"
#define ZYGOTE_SYSCALL_TRACE_FILE "/data/local/tmp/zygote_strace.txt"
#define STRACE_PATH "/data/local/tmp/strace"
#define WHITELIST_FILE "/data/local/tmp/whitelist.txt"

typedef struct process PROCESS;


void strace(int pid, char *outputFile)
{
	const int MAX_COMMAND_LENGTH = 100;

    char straceCommand[MAX_COMMAND_LENGTH];
    snprintf(straceCommand, MAX_COMMAND_LENGTH, "su -c \"%s -p %d -o %s\" &", STRACE_PATH, pid, outputFile);
    if(!fork()){
        system(straceCommand);
    }
}


char* getProcName(int pid)
{
	const int PATH_MAX_LENGTH = 40;
	const int LINE_MAX_LENGTH = 20;
	const int WHITESPACE_SIZE = 1;
	const char NAME[] = "Name:";
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

    while(fgets(line, LINE_MAX_LENGTH, statusf)) {
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

int findZygotePid()
{
	const int MAX_PID_SEARCH = 1000;
	const char ZYGOTE[] = "zygote";
	int pid = 1;
    char* output;

    for (pid=1; pid<MAX_PID_SEARCH; pid++){
	    output = getProcName(pid);

        if (output != NULL && strncmp(output, ZYGOTE, strlen(ZYGOTE)) == 0) {
            //printf("zygote name returned is %s\n", output);
            return pid;
        }
	}
}

void watchAndStraceZygote()
{
    //system("rm -f %s", ZYGOTE_SYSCALL_TRACE_FILE);
    int pid = findZygotePid();

    char *straceOutput = ZYGOTE_SYSCALL_TRACE_FILE;
    strace(pid, straceOutput);
    printf("zygote pid is %d\n", pid);
}

int main(int argc, char **argv){
    watchAndStraceZygote();
}