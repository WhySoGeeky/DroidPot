#include "zygotew.h"

#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <android/log.h>


#define LOG_TAG "Zygote watchdog"
#define ZYGOTE_SYSCALL_TRACE_FILE "/data/local/tmp/zygote_strace.txt"
#define WHITELIST_FILE "/data/local/tmp/whitelist.txt"


typedef struct process PROCESS;

struct process MONITORED_PROCESSES[100]; //remember to clear the memory
int monitored_proc_count = 0;


void strace(int pid, char *outputFile) 
{
	const int MAX_COMMAND_LENGTH = 100;

    char straceCommand[MAX_COMMAND_LENGTH];
    snprintf(straceCommand, MAX_COMMAND_LENGTH, "su -c \"strace -p %d -o %s\" &", pid, outputFile);
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


void watchAndStraceZygote()
{
    system("rm -f %s", ZYGOTE_SYSCALL_TRACE_FILE);
    int pid = findZygotePid();

    char *straceOutput = ZYGOTE_SYSCALL_TRACE_FILE;
    strace(pid, straceOutput);
    printf("zygote pid is %d\n", pid);
}

void monitorProcessForkIfExist()
{
	const int PATH_MAX_LENGTH = 300;
	const int LINE_MAX_LENGTH = 100;
	const int WHITESPACE_SIZE = 1;
	const char FORK[] = "fork()";

    char path[PATH_MAX_LENGTH], line[LINE_MAX_LENGTH], *p;
    FILE* stracef;

    snprintf(path, PATH_MAX_LENGTH, ZYGOTE_SYSCALL_TRACE_FILE);
    stracef = fopen(path, "r");

    if(!stracef)
        return;

    while(fgets(line, LINE_MAX_LENGTH, stracef)) {

        if (strncmp(line, FORK, strlen(FORK)) != 0)
            continue;

        p = line + strlen(FORK) + WHITESPACE_SIZE;
        while(isspace(*p)) {
        	++p;
        }
        //remove "= "
        ++p;
        ++p;
        
        char *pid = p;
        printf("found forked process. PID %s\n", pid);

        //PROBLEM HERE!!! BUG!!!!!!!!! overflow issue
        int isWhitelisted = checkAgainstWhitelist(pid);   
        if (!isWhitelisted ) { //check if it's not whitelisted and not monitored at the moment
            printf("white list if statement\n");
            char straceProcessResult[PATH_MAX_LENGTH];
            char *process_name = getProcName(atoi(pid));
            if (process_name == NULL) {
                break;
            }
            printf("procName (testing) is %s\n", process_name);
            snprintf(straceProcessResult, PATH_MAX_LENGTH, "/data/local/tmp/strace_%s", process_name);
            printf("strace file is %s \n",straceProcessResult);
            /*
            //create process struct
            struct process proc;
            proc.pid = pid;
            proc.name = procName;
            printf("here\n");
            //check if already monitored
            int isAddedToMonitorList = addToMonitoringListIfNotExist(proc);
            printf("here2\n");
            if (isAddedToMonitorList) {
            	printf("Monitoring new process %s\n",proc.name);
            	strace(atoi(p), straceProcessResult);
            } else {
            	printf("Process %s already under monitoring\n",proc.name);
            }
            */
            //
            //
            //
            //other monitors will be started here.
        	//
        	//
        	//
        }
        //break;
    }
    fclose(stracef);
}

int addToMonitoringListIfNotExist(struct process proc)
{
	int i=0;
	//check for existing processes first
	for (i=0; i < sizeof(MONITORED_PROCESSES); i++){
		struct process monitored_proc; 
		monitored_proc.name = MONITORED_PROCESSES[i].name;
		monitored_proc.pid = MONITORED_PROCESSES[i].pid;

		if (strncmp(monitored_proc.name, proc.name, strlen(proc.name)) == 0){
			if (strncmp(monitored_proc.pid, proc.pid, strlen(proc.pid)) == 0){
				//process already under monitored
				return 0;
			}else {
				//monitored process change PID
				MONITORED_PROCESSES[i] = proc;
				return 1;
			}
			
		}
	}

	MONITORED_PROCESSES[monitored_proc_count] = proc;
	monitored_proc_count +=1;
	return 1;

}

int checkAgainstWhitelist(char *pid)
{
	const int PATH_MAX_LENGTH = 40;
	const int LINE_MAX_LENGTH = 100;
	const int WHITESPACE_SIZE = 1;

    //printf("checkAgainstWhitelist function, process name is %s\n", processName);
    printf("checking against white list for %s...\n", pid);
    char *processName = getProcName(atoi(pid));

    if (processName == NULL){
        return 0;
    }

    //read from whitelist file and compare process name
    char path[PATH_MAX_LENGTH], line[LINE_MAX_LENGTH], *p;
    FILE* whitelistf;

    snprintf(path, PATH_MAX_LENGTH, WHITELIST_FILE);
    whitelistf = fopen(path, "r");
    //printf("opening white list at %s\n", path);

    //check if file exist
    if(!whitelistf){
        printf("whitelist file not found\n");
        return NULL;
    }

    while(fgets(line, LINE_MAX_LENGTH, whitelistf)){
        //printf("line is %s\n", line);
        if(strncmp(line, processName, strlen(processName)) != 0){
            continue;
        }else {
            //printf("process inside whitelist\n");
            return 1;
        }
    }
    printf("process not inside whitelist\n");
    return 0;
}



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



int findZygotePid()
{
	const int MAX_PID_SEARCH = 1000;
	const char ZYGOTE[] = "zygote";
	int pid = 1;
    char* output;
	
    for (pid=1; pid<MAX_PID_SEARCH; pid++){
	    output = getProcName(pid);
        //printf("output is %s\n", output);

        if (output != NULL && strncmp(output, ZYGOTE, strlen(ZYGOTE)) == 0) {
            //printf("found zygote\n");
            //printf("zygote name returned is %s\n", output);
            return pid;
        }
	}
}

int main(int argc, char **argv)
{

	//LOGI("Zygote watchdog started");
    watchAndStraceZygote();
	while(1){
        //printf("watching...\n");
		sleep(1);
		monitorProcessForkIfExist();
	}

	//findZygotePid();
}