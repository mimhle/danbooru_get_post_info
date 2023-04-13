# danbooru_get_post_info
This script is used to get the post information from danbooru.donmai.us. It will get the post information from the post id and save it to a json file in the same directory as the script.
## Usage
### First, you need to install the required packages.
```pip install requests tqdm```
### Then, you can run the script.
```python danbooru_get_post_info.py <start> [<stop>] [-t <timeout>] [-r <retry>]```
### Arguments
* start: The start post id.
* stop: The stop post id, if not specified, it will be the same as start.
* -t, timeout: The timeout for all request in seconds. Default is 3600.
* -r, retry: The retry times for each request. Default is 10.
* -h, --help: Show the help message and exit.
### Output
The output file will be named as `<start>-<stop>.json` if stop is specified, or `<start>.json` if stop is not specified.
The output file will be saved in the same directory as the script.
## Contributing
This project is open to contributions. If you want to contribute, feel free to open an issue or pull request.
## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
