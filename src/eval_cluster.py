import argparse
import os
import time
import numpy as np
import networkx as nx
from typing import Tuple

from sched_lib.file_handling_helper import read_dag
from sched_lib.processors.homogeneous.cluster import CluesteredProcessor
from sched_lib.algorithms.static.HEFT import HEFT_cluster
from sched_lib.algorithms.static.QLHEFT import QLHEFTToClusteredProcessor
from sched_lib.algorithms.static.CQGAHEFT import CQGAHEFT
from sched_lib.algorithms.static.HTSTC import HTSTC
from sched_lib.algorithms.static.HTSTC import HTSTCListSchedulerToClusteredProcessor
from sched_lib.scheduler.list_scheduler import ListSchedulerToClusteredProcessor
from sched_lib.algorithms.dag_utils import convert_to_specified_ccr_dag
from sched_lib.algorithms.static.num_learn import num_learn


def option_parser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--dag_file_path',
                            required=True,
                            type=str,
                            help='path to dag file (.tgff, .yaml, .json, or , .dot)')
    arg_parser.add_argument('--algorithm',
                            required=True,
                            type=str,
                            choices=['HEFT', 'QL-HEFT', 'CQGA-HEFT', 'HTSTC'],
                            help='Algorithm name used for evaluation.')
    arg_parser.add_argument('--num_of_clusters',
                            required=True,
                            type=int,
                            help='Number of clusters in a clustered many-core processor.')
    arg_parser.add_argument('--num_of_cores',
                            required=True,
                            type=int,
                            help='Number of cores in a single cluster.')
    arg_parser.add_argument('--inout_ratio',
                            required=True,
                            type=float,
                            help='Ratio of communication time outside the cluster to \
                                  communication time inside the cluster for clustered many-core processor.')
    arg_parser.add_argument('--ccr',
                            required=False,
                            type=float,
                            help='CCR value of DAG.')
    arg_parser.add_argument('--write_makespan',
                            required=False,
                            action='store_true',
                            help='Write out the makespan in the log.')
    arg_parser.add_argument('--write_duration',
                            required=False,
                            action='store_true',
                            help='Write out the duration in the log.')
    arg_parser.add_argument('--dest_file_path',
                            required=True,
                            type=str,
                            help='path to result file.')
    args = arg_parser.parse_args()

    return args.dag_file_path, args.algorithm, args.num_of_clusters, args.num_of_cores, args.inout_ratio, args.ccr, args.dest_file_path, args.write_makespan, args.write_duration


def main(dag_file_path, alg, num_clusters, num_cores, inout_ratio, ccr, dest_file_path, write_makespan, write_duration):
    G = read_dag(dag_file_path)
    if(ccr):
        convert_to_specified_ccr_dag(G, ccr)
    P = CluesteredProcessor(num_clusters, num_cores, inout_ratio)
    log_str = os.path.basename(dag_file_path)

    if(alg == 'HEFT'):
        start_time = time.time()
        sched_list = HEFT_cluster(G, P.inout_ratio)
        duration = time.time() - start_time
        if(write_duration):
            log_str += f',{duration}'
        S = ListSchedulerToClusteredProcessor(G, P, sched_list)
        S.schedule()
    elif(alg == 'QL-HEFT'):
        qlheft = QLHEFTToClusteredProcessor(G, 1.0, 0.2, P.inout_ratio)
        qlheft.learn(num_learn[str(G.number_of_nodes())])
        if(write_duration):
            log_str += f',{qlheft.learning_log["duration"]}'
        sched_list = qlheft.get_sched_list()
        S = ListSchedulerToClusteredProcessor(G, P, sched_list)
        S.schedule()
    elif(alg == 'CQGA-HEFT'):
        cqgaheft = CQGAHEFT(G, 8, 30, 0.01, 1.0, 0.2, P)
        cqgaheft.evolution()
        if(write_duration):
            log_str += f',{cqgaheft.duration}'
        sched_list = cqgaheft.get_sched_list()
        S = ListSchedulerToClusteredProcessor(G, P, sched_list)
        S.schedule()
    elif(alg == 'HTSTC'):
        start_time = time.time()
        htstc = HTSTC(G, P.inout_ratio)
        sched_list = htstc.get_sched_list()
        for node_i, succ_i in htstc.merge_list:
            HTSTC.merge_two_nodes(G, node_i, succ_i)
        S = HTSTCListSchedulerToClusteredProcessor(G, P, sched_list)
        duration = time.time() - start_time
        if(write_duration):
            log_str += f',{duration}'
        S.schedule_using_task_duplication()

    # Write result
    if(write_makespan):
        log_str += f',{S.get_makespan()}'
    f = open(dest_file_path, "a")
    f.write(log_str + "\n")
    f.close()


if __name__ == '__main__':
    dag_file_path, alg, num_clusters, num_cores, inout_ratio, ccr, dest_file_path, write_makespan, write_duration = option_parser()
    main(dag_file_path, alg, num_clusters, num_cores, inout_ratio, ccr, dest_file_path, write_makespan, write_duration)
