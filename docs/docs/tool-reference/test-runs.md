You can call the `test` function to mimic a Toolchest run. 

`test` actually uploads your inputs to Toolchest's infrastructure. Nothing is done to the files beyond the upload.

Function Call
=============

```python
tc.test(
  	inputs,
  	output_path=None,
  	tool_args="",
  	is_async=False,
)
```

Output Files
------------

`test` has one output file, `test_output.txt`, a text document that reads:

```
success
```