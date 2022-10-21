# Asynchronous Runs

Toolchest supports async execution for every tool. Async runs are useful long running commands, because you do not need to keep an open terminal or connection while Toolchest is executing.

We've seen people use async runs from AWS Lambda functions, custom automated pipelines, and manual calls from IDEs.

## Launching an Async Run

To launch an async run, ad the **`is_async`** parameter with the value **True** in your function call. For example, 
using the `test` function:

```python
my_run = tc.test(
    inputs="./",
    output_path="./output",
  	is_async=True,
)
```

After the Toolchest run is initialized and all file transfers are complete, the Toolchest call returns an 
[output object](output-objects.md) containing a run ID.

You can check your run status using the returned run ID (e.g. `my_run.run_id`).


Once you see this, Toolchest is executing your run in the background, and you're safe to close your terminal. (Be sure 
to record the run ID!)

## Checking Run Status

To check the status of your async run, call the **`get_status`** function with your run ID.

```python
print(tc.get_status(run_id="YOUR_RUN_ID"))
'executing'
```

**`get_status`** returns a string. Once the status is `ready_to_transfer_to_client`, the run has finished execution and 
is ready to download.

### Statuses enum

There's an enum –`Status` – that contains all statuses returned from `get_status()`. You can check statuses against 
this enum for custom error handling, progress tracking, or whatever you're building.

```python
status = tc.get_status(run_id="YOUR_RUN_ID")
if status == tc.Status.COMPLETE:
  print("AlphaFold run finished! Sending email to researcher...")
```

To check all possible enum values, you can print the enum as a list:

```python
print(list(tc.Status))
[<Status.INITIALIZED: 'initialized'>, ...
```

## Downloading Output

To download the output manually, call the **`download`** function with your run ID and output directory.

```python
tc.download(
  	run_id="YOUR_RUN_ID", 
  	output_path="./output/",
)
```


This downloads the run's output file(s) into the output directory. You can run `download` for 7 days after starting the 
run.
