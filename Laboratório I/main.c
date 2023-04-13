#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/wait.h>


typedef struct _process {
    pid_t pid;
    int pipe[2];
    long ini;
    long fim;
} process_p;

typedef struct _intervalos {
    long ini;
    long fim;
} interval_p;

typedef struct _send_thread {
    int *v;
    interval_p *intervalos;
    long ini;
    long fim;
    long n;
    long p;
} send_thread_p;

typedef struct _send_thread_ordena {
    int *v;
    long ini_ord;
    long fim_ord;
} send_thread_ordena_p;


int *criar_vetor(long n);
void ordenar_vetor(int *v, long ini, long fim);
interval_p *separa_intervalos(long n, long p);
void lancando_processos_ordenacao(int *v, interval_p *intervalos, long n, long p);
void lancando_processos_ordenacao_thread(int *v, interval_p *intervalos, long n, long p);
void concatena_vetor(int *v, interval_p *intervalos, long n, long p);
void *ordenar_vetor_thread(void *arg);
void * concatena(void *arg);

void print_lista(int *v, long n);
void print_lista_intervalo(int *v, long ini, long fim);
void verificar_ordenacao(int *v, long ini, long fim);


void main(int argc, char *argv[]){
    long n_elementos = atol(argv[1]), n_processos = atol(argv[2]);
    int *v = criar_vetor(n_elementos);

    printf("Iniciando ordenação elementos: %ld, n_processos: %ld \n", n_elementos, n_processos);

    interval_p *intervalos = separa_intervalos(n_elementos, n_processos);

        // Faz uso de fork e pipe
    //lancando_processos_ordenacao(v, intervalos, n_elementos, n_processos);

        // Faz uso de threads
    lancando_processos_ordenacao_thread(v, intervalos, n_elementos, n_processos);
    
        // Faz uso de threads
    concatena_vetor(v, intervalos, n_elementos, n_processos);

    verificar_ordenacao(v, 0, n_elementos);
    //print_lista(v, n_elementos);

    exit(0);
}


int *criar_vetor(long n){
    int *r = malloc(sizeof(int)*n);
    srand(time(NULL));

    for(long i = 0; i < n; i++)
        r[i] = rand() % 100;

    return r;
}

interval_p *separa_intervalos(long n, long p){
    long ini=0, fim=0, a=(n/p), b=(n%p);
    interval_p *r = malloc(sizeof(interval_p)*p);

    for(long i = 0; i < p; i++){
        ini = fim;
        fim += a;
        if(b > 0){
            fim++;
            b--;
        }

        r[i].ini = ini;
        r[i].fim = fim;
    }

    return r;
}


    //selection sort
void ordenar_vetor(int *v, long ini, long fim){
    long i, j, min, aux;

    printf("iniciando ordenação pid: %d \n", getpid());
    for (i = ini; i < (fim-1); i++){
        min = i;

        for (j = (i+1); j < fim; j++) {
            if(v[j] < v[min])
                min = j;
        }

        if (v[i] != v[min]) {
            aux = v[i];
            v[i] = v[min];
            v[min] = aux;
        }
    }
    printf("finalizando ordenação pid: %d \n", getpid());
}

    //selection sort
void *ordenar_vetor_thread(void *arg){
    send_thread_ordena_p *s = (send_thread_ordena_p*) arg;
    long i, j, min, aux, ini = (s->ini_ord), fim = (s->fim_ord);
    //printf("Ordenando intervalo: (%ld - %ld) \n", (s->ini_ord), (s->fim_ord));

    printf("iniciando ordenação pid: %d \n", getpid());
    for (i = ini; i < (fim-1); i++){
        min = i;

        for (j = (i+1); j < fim; j++) {
            if(s->v[j] < s->v[min])
                min = j;
        }

        if (s->v[i] != s->v[min]) {
            aux = s->v[i];
            s->v[i] = s->v[min];
            s->v[min] = aux;
        }
    }
    printf("finalizando ordenação pid: %d \n", getpid());
}

    // fork e pipe
void lancando_processos_ordenacao(int *v, interval_p *intervalos, long n, long p){
    process_p *pid_filho = malloc(sizeof(process_p)*p);
    pid_t pid;
    long index;
    int status, *aux = malloc(sizeof(int)*n);

    for(long i = 0; i < p; i++){
        pid_filho[i].ini = intervalos[i].ini;
        pid_filho[i].fim = intervalos[i].fim;
    }


        // Inicia a execução paralela
    for(long i = 0; i < p; i++){
        index = i;
        pipe(pid_filho[index].pipe);
        pid = fork();

        if(pid != 0){
            pid_filho[i].pid = pid;
        } else break;
    }

        // Execução do novo processo
    if(pid == 0){
        ordenar_vetor(v, pid_filho[index].ini, pid_filho[index].fim);
        printf("Escrevendo \n");

        close(pid_filho[index].pipe[0]);
        write(pid_filho[index].pipe[1], v, (sizeof(int)*n));
        close(pid_filho[index].pipe[1]);

        //print_lista_intervalo(v, pid_filho[index].ini, pid_filho[index].fim);
        printf("Processo: %d concluído \n", pid);

        _exit(EXIT_SUCCESS);
        

        // Controla os processos
    } else {
        //for(int i = 0; i < p; i++) printf("(%d-%d) ", pid_filho[i].ini, pid_filho[i].fim);
        //printf("\n");

            // Receber dados
        for(long i = 0; i < p; i++){
            printf("Aguardando \n");
            wait(&status);
            if(!WIFEXITED(status)){
                printf("Erro no processo filho.");
            }

            printf("Recebendo \n");

            close(pid_filho[i].pipe[1]);
            read(pid_filho[i].pipe[0], aux, (sizeof(int)*n));
            close(pid_filho[i].pipe[0]);

            //print_lista_intervalo(aux, pid_filho[i].ini, pid_filho[i].fim);


            for(long j = pid_filho[i].ini; j < pid_filho[i].fim; j++)
                v[j] = aux[j];
            
            //verificar_ordenacao(v, pid_filho[i].ini, pid_filho[i].fim);
            //printf("Processo: %d || PID: %d ||  Valor: %d \n", procs[i].id, procs[i].pid, var);    
        }  
    }

    free(aux);
}

    // thread
void lancando_processos_ordenacao_thread(int *v, interval_p *intervalos, long n, long p){
    pthread_t *threads = malloc(sizeof(pthread_t)*p); 
    send_thread_ordena_p *s = malloc(sizeof(send_thread_ordena_p)*p);

    for(long i = 0; i < p; i++){
        s[i].v = v;
        s[i].ini_ord = intervalos[i].ini;
        s[i].fim_ord = intervalos[i].fim;
        pthread_create(&threads[i], NULL, ordenar_vetor_thread, (void *)(&s[i]));
    }

    for(long i = 0; i < p; i++){
        pthread_join(threads[i], NULL);
    }
}

void concatena_vetor(int *v, interval_p *intervalos, long n, long p){
    pthread_t t;
    long ini = 0, fim = p;
    send_thread_p s = {v, intervalos, ini, fim-1, n, p};

    pthread_create(&t, NULL, concatena, (void *)(&s));
    pthread_join(t, NULL);

    //print_lista(v, n);
}

void *concatena(void *arg){
    pthread_t t1, t2;
    send_thread_p *s = (send_thread_p*) arg;

    printf("iniciando concatenação (%ld-%ld) \n", (s->ini), (s->fim));
    if ((s->ini) != (s->fim)){
        int i, j, k, *aux, mid = ((s->fim)-(s->ini)+1) / 2;

        send_thread_p s1 = {(s->v), (s->intervalos), (s->ini), (s->ini)+mid-1, (s->n), (s->p)};
        send_thread_p s2 = {(s->v), (s->intervalos), (s->ini)+mid, (s->fim), (s->n), (s->p)};

        pthread_create(&t1, NULL, concatena, (void *)(&s1));
        pthread_create(&t2, NULL, concatena, (void *)(&s2));

        pthread_join(t1, NULL);
        pthread_join(t2, NULL);

        int t1_n_ini = s->intervalos[(s1.ini)].ini;
        int t1_n_fim = s->intervalos[(s1.fim)].fim;
        int t2_n_ini = s->intervalos[(s2.ini)].ini;
        int t2_n_fim = s->intervalos[(s2.fim)].fim;

        printf("concatendo (%ld-%ld) | intervalo (%ld-%ld) - (%ld-%ld) \n", (s->ini), (s->fim), t1_n_ini, t1_n_fim, t2_n_ini, t2_n_fim);

        aux = malloc(sizeof(int)*(t2_n_fim-t1_n_ini));

        i = t1_n_ini;
        j = t2_n_ini;
        k = 0;
        while((i < t1_n_fim) || (j < t2_n_fim)){
            if((i < t1_n_fim) && (j < t2_n_fim)){
                if((s->v)[i] < (s->v)[j]){
                    aux[k] = (s->v)[i];
                    i++;
                    k++;     

                } else {
                    aux[k] = (s->v)[j];
                    j++;
                    k++;
                }

            } else if(i < t1_n_fim){
                aux[k] = (s->v)[i];
                i++;
                k++;
                
            } else {
                aux[k] = (s->v)[j];
                j++;
                k++;
            }
        }

        for(i = t1_n_ini, j= 0; i < t2_n_fim; i++, j++){
            (s->v)[i] = aux[j];
        }

        free(aux);
    }
    printf("finalizando concatenação (%ld-%ld) \n", (s->ini), (s->fim));
}


void print_lista(int *v, long n){
    for(int i = 0; i < n; i++)
        printf("%d - ", v[i]);
    
    printf("\n");
}

void print_lista_intervalo(int *v, long ini, long fim){
    for(int i = ini; i < fim; i++)
        printf("%ld - ", v[i]);
    
    printf("\n");
}

void verificar_ordenacao(int *v, long ini, long fim){
    bool res = true;
    for(long i = ini; i < fim-1; i++){
        if(v[i] > v[i+1]){
            res = false;
            //printf("Erro \n");
        }
    }

    if(res) printf("Vetor ordenado corretamente \n");
    else printf("Erro na ordenação do vetor \n");
}