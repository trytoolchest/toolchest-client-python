Sometimes, there's no alternative to downloading a terabyte of data from an FTP or HTTPS source. When the source 
download speed is 5 MB/s (looking at you, NCBI RefSeq and EMBL!), the transfer takes days – a long time to keep your 
laptop up and running.

`transfer` moves files from any supported input location to any supported output location. It runs in the background, 
meaning you don't need to keep your laptop or server running during transfer.

# Function Call

```python
tc.transfer(
  	inputs,
  	output_path=None,
  	is_async=True,
)
```

## Function Arguments


| Argument      | Description                                                                                                                                                                                                                   |
| :------------ |-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `inputs`      | Path to a file that will be passed in as input. All formats supported by `ffmpeg` are allowed. The files can be a local or remote, see [Using Files](../getting-started/using-files.md).                                      |
| `output_path` | (optional) Path (directory) to where the output files will be downloaded. The path can be a local or remote, see [Using Files](../getting-started/using-files.md).                                                            |
| `is_async`    | Whether to run the job asynchronously. By default, this is true. If you set this to false, the Toolchest command will wait to exit until the transfer is complete. See [Async Runs](../feature-reference/async-runs.md) for more. |
