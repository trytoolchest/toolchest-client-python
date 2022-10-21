# Output Objects

Every Toolchest run returns an object containing the run ID (`run_id`), local paths to downloaded output files 
(`output_path`), and more.

As an example, we'll use the output from this `test` function call, but you can do this for any Toolchest tool:

```python
import toolchest_client as tc

toolchest_output = tc.test(
    inputs="./",
    output_path="./output/",
    tool_args="",
)
```

##  Run Metadata

The **`run_id`** instance variable contains the ID of the Toolchest run, stored as a string. 

Likewise, the **`output_path`** instance variable contains local paths to downloaded output files.

```python
>>> toolchest_output.run_id
'00000000-0000-0000-0000-000000000000'  # this will be your custom run ID
>>> toolchest_output.output_path
'OUTPUT_DIR/test_output.txt'
```

You can store and use the `run_id` check the run's status with [Async Runs](async-runs.md).

`output_path` will be a string (for 1 output file), a list of strings (for multiple output files), or a null value (if 
download was skipped).

## Download

You can also directly call the **`download`** function from the output object to download (or re-download) the outputs. 

```python
toolchest_output.download(
  	output_path="./",
)
```

However, keep in mind that Toolchest only retains your job's output for 7 days after job execution.