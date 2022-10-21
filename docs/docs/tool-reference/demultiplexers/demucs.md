**demucs** is a demultiplexing tool for audio source separation. To learn more about the tool, check out its 
[GitHub repo](https://github.com/facebookresearch/demucs).

Function Call
=============

```python
tc.demucs(
  	inputs,
  	output_path=None,
  	tool_args="",
  	is_async=False,
)
```

Function Arguments
------------------

See the Notes section below for more details.

| Argument      | Use in place of:    | Description                                                                                                                                                                                                                |
| :------------ | :------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `inputs`      | `--input`           | Path to a file that will be passed in as input. All formats supported by `ffmpeg` are allowed. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md).        |
| `output_path` | `--output`          | (optional) Path (directory) to where the output files will be downloaded. If omitted, skips download. The files can be a local or remote, see [Using Files](../../getting-started/using-files.md). |
| `tool_args`   | all other arguments | (optional) A string containing additional arguments to be passed to Demucs, formatted as if using the command line.                                                                                                        |
| `is_async`    |                     | Whether to run a job asynchronously.  See [Async Runs](../../feature-reference/async-runs.md) for more.                                                                                                                                    |

Tool Versions
=============

Toolchest supports version **3.0.4** of Demucs.

Supported Additional Arguments
==============================

- \-v
- \--verbose
- \--shifts
- \--overlap
- \-no-split
- \--two-stems
- \--int24
- \--float32
- \--clip-mode
- \--mp3
- \--mp3-bitrate
- \-n

Set additional arguments with `tool_args`. For example: `tool_args="-n mdx_extra --shifts=5"`