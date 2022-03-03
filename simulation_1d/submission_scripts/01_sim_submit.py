#!/usr/bin/python
import platform, sys, os, re, subprocess, time
import numpy as np
os.chdir("/Users/mengbing/Documents/research/RL_nonstationary/cumsumrl/simulation_1d/submission_scripts")
sys.path.append("/Users/mengbing/Documents/research/RL_nonstationary/cumsumrl/simulation_1d/submission_scripts")

#%% create slurm scripts
settings = [["homo","pwconst2"], ["homo","smooth"], ["pwconst2","homo"], ["smooth","homo"]]
os.system("bash 01_sim_create_submissions.sh")
gammas = [0.9,0.95]
gamma_names = [re.sub("\.", "", str(gamma)) for gamma in gammas]
Ns = [25,100]
n_random_seeds = 4
kappa_list = np.arange(25, 76, step=5)
kappa_list = kappa_list[::-1]
njobs = 0
n_jobs_running = 0
cmd_job = ["squeue", "-u", "mengbing"] # !!change to your account name
error_handling1 = """exitStatus=1; while [[ "$exitStatus" == "1" ]]; do sleep 10; """
error_handling2 = """exitStatus=$?; done"""
for N in Ns:
    for setting in settings:
        trans_setting = setting[0]
        reward_setting = setting[1]
        for i in range(len(gammas)):
            gamma = gammas[i]
            gamma_name = gamma_names[i]
            for kappa in kappa_list:
                for seed in range(1, n_random_seeds + 1):

                    # if ((setting == ["smooth","homo"] and gamma == 0.9 and kappa >= 75)):
                    #     continue

                    job_name = '01_sim_1d_trans' + trans_setting + '_reward' + reward_setting + '_gamma' + gamma_name +\
                                '_kappa' + str(kappa) + '_N' + str(N) + '_' + str(seed) + '_run.slurm'
                    cmd = error_handling1 + "sbatch " + job_name + "; " + error_handling2

                    print("Submitting Job with command: %s" % cmd)
                    status = subprocess.check_output(cmd, shell=True)
                    time.sleep(10)
                    jobnum = [int(s) for s in status.split() if s.isdigit()][0]
                    print("Job number is %s" % jobnum)

                    # check the number of running jobs
                    job_status = subprocess.check_output(cmd_job)
                    time.sleep(10)

                    jobs_running = job_status.split(b'\n')[1:-1]
                    n_jobs_running = len(jobs_running)
                    # find array jobs
                    array_jobs = [len(job_running.split(b'[')) for job_running in jobs_running]
                    n_array_jobs = sum(array_job == 2 for array_job in array_jobs)

                    # if more than 4 array jobs or 1000 individual jobs are running simutaneously, we will wait
                    # until they finish (in case the cluster does not allow for submitting too many jobs at once)
                    while n_array_jobs > 4 or n_jobs_running >= 1000:
                        time.sleep(20)
                        job_status = subprocess.check_output(cmd_job)
                        jobs_running = job_status.split(b'\n')[1:-1]
                        n_jobs_running = len(jobs_running)
                        array_jobs = [len(job_running.split(b'[')) for job_running in jobs_running]
                        n_array_jobs = sum(array_job == 2 for array_job in array_jobs)

                    njobs += 1

    print("\nCurrent status:\n")
    #show the current status
    os.system("squeue -u mengbing")
