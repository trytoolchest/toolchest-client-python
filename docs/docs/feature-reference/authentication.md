# Authentication

To run Toolchest jobs, you'll need a Toolchest key. If you don't have one yet, you can get a key 
[here](https://airtable.com/shrKzQNuDHrGkEAI2).

## Setting a Key

Use the **`set_key`** function to authenticate your Toolchest calls:

```python
import toolchest_client as tc
tc.set_key("YOUR_TOOLCHEST_KEY")
```

`YOUR_TOOLCHEST_KEY` should be a string containing either the key value or a path to a file containing the key.

You can also set your key through the `TOOLCHEST_KEY` environment variable.

## Getting a Stored Key

To check the value of the key in use, use the **`get_key`** function, which returns a string containing your key value.

```python
import toolchest_client as tc
tc.get_key()
```

## Private Tools and Databases

If you'd like to use a private tool database with Toolchest without exposing it to the public, Toolchest supports 
restricting some databases and tools to your account.