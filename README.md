# Scheduling_Simulator
# Setup Flow
Clone this repository to your own workspace.
```
git clone https://github.com/azu-lab/Scheduling_Simulator.git
cd Scheduling_Simulator
./setup.bash
```

# Uninstall Flow
```
./uninstall.bash  # if you want to remove installed packages.
cd ../
rm -rf Scheduling_Simulator
```


# Evaluation Command
These command is used to evaluate the algorithm by varying the parameters.
The supported [Algorithm Name] are as follows.
- HEFT
- HTSTC
- QL-HEFT
- CQGA-HEFT (Proposed algorithm)

Note that these commands are scheduled for many DAGs and will take time to complete.

## Evaluation of varying the CCR values

```
cd ./src/evaluation && bash eval_change_ccr.bash --num_of_clusters 2 --num_of_cores 16 --inout_ratio 3.0 --write_makespan --write_duration -a [Algorithm Name] --ccr [CCR]
```

## Evaluation of varying the ratio of communication time outside the CC to communication time within the CC
```
cd ./src/evaluation && bash eval_change_inout_ratio.bash --num_of_clusters 2 --num_of_cores 16 --write_makespan --write_duration -a [Algorithm Name] --inout_ratio [Ratio]
```


## Evaluation of varying the number of tasks in a DAG
```
cd ./src/evaluation && bash eval_change_num_of_tasks.bash --num_of_clusters 2 --num_of_cores 16 --inout_ratio 3.0 --write_makespan --write_duration --root_dag_dir ./DAGs -a [Algorithm Name]
```

# Results
The result of executing the above command is stored in `Scheduling_Simulator/src/result/`.
Once the command has been completed, the following commands can be used to create a box-and-whisker diagram.

## Visualization results of varying the CCR values
```
cd ./src/evaluation && python3  box_plot.py --source_result_dir ./result/change_ccr --ylabel 'Makespan' --xlabel 'CCR' --format png --dest_dir ./figure --normalized_by_median QL-HEFT
```

## Visualization results of varying the ratio of communication time outside the CC to communication time within the CC
```
cd ./src/evaluation && python3  box_plot.py --source_result_dir ./result/change_inout_ratio --ylabel 'Makespan' --xlabel 'Ratio' --format png --dest_dir ./figure --normalized_by_median QL-HEFT
```

## Visualization results of varying the number of tasks in a DAG
```
cd ./src/evaluation && python3  box_plot.py --source_result_dir ./result/change_num_of_tasks --ylabel 'Makespan' --xlabel 'Number of tasks' --format png --dest_dir ./figure --normalized_by_median QL-HEFT
```

## Visualization results of the comparison between algorithms
```
cd ./src/evaluation && python3  comparison_box_plot.py --source_result_dir ./result/[Result dir] --comparison_base [Algorithm Name 1] --comparison [Algorithm Name 2] --ylabel 'Makespan' --xlabel [X] --format png --dest_dir ./figure
```
