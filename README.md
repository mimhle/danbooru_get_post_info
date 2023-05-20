# danbooru_get_post_info
This script is used to get the post information from danbooru.donmai.us. It will get the post information from the post id and save it to a json file in the same directory as the script.
## Usage
### Install the required packages.
Requires Python 3.10 or above.

```pip install -r requirements.txt```
### Then, you can run the script.
```python danbooru_get_post_info.py <start> [<stop>] [-t <timeout>] [-r <retry>]```
### Arguments
* start: The start post id.
* stop: The stop post id, if not specified, it will be the same as start.
* -f, --file: The file containing the post ids. If not specified, it will be <start>-<stop>.json if stop is specified, or <start>.json if stop is not specified.
* -t, --timeout: Timeout in seconds for each request. Default is 300 seconds.
* -r, --retry: The retry times for each request. Default is 100.
* --cooldown: Cooldown in seconds finishing each request. Default is 1 second.
* --concurrency: Max concurrent requests. Default is 5.
* -h, --help: Show the help message and exit.
### Output
The output file will be named as `<start>-<stop>.json` if stop is specified, `<start>.json` if stop is not specified or according to the file name specified with `-f`.
The output file will be saved in the same directory as the script.
## Contributing
This project is open to contributions. If you want to contribute, feel free to open an issue or pull request.
## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
