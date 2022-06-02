import os
import sys

import sentry_sdk

from toolchest_client.tools import Kraken2

from toolchest_client.tools.tool_args import TOOL_ARG_LISTS

sentry_sdk.set_tag('send_page', False)


def parse_tool(args):
    tool_name = args[1]
    print(args)
    print(args[2:])
    if tool_name == 'kraken2':
        allowed_tool_args = TOOL_ARG_LISTS['kraken2']['whitelist']
        split_args = args[2:]
        tool_args = ""
        inputs = []
        output_path = None
        database_name = "standard"
        database_version = "1"
        custom_database_path = None
        i = 0
        while i < len(split_args):
            arg = split_args[i]
            if arg in allowed_tool_args:
                follow_count = allowed_tool_args[arg]
                while follow_count > 0:
                    i += 1
                    arg = arg + split_args[i]
                    follow_count -= 1
                tool_args += ' ' + arg
            elif ".f" in arg:
                inputs.append(arg)
            elif arg == '-db':
                i += 1
                db = split_args[i]
                print(f'db: {db}')
                if db.startswith('s3://'):
                    custom_database_path = db
                else:
                    database_name = db
            elif arg == '--report':
                i += 1
                output_path = os.path.abspath(os.path.dirname(split_args[i]))
            elif arg == '>':
                break
            else:
                print(f"Argument {arg} is being dropped as it is either not allowed or not recognized")
            i += 1
        k = Kraken2(tool_args, 'output.tar.gz', inputs, output_path, database_name, database_version,
                    custom_database_path)
        out = k.run()
        return out


parse_tool(sys.argv)
