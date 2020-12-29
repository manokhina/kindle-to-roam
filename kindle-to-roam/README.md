# kindle-to-roam
Generates Roam Research pages from Kindle clippings.

## Usage
Clone the repo and go to the tool directory:
```
git clone https://github.com/manokhina/kindle-to-roam.git
cd kindle-to-roam
```
Connect your Kindle to the computer. If you have a Mac, run:
```
python3 generate_roam.py
```
If you have another OS, specify Kindle clippings path with a `clippings_path` parameter, for example:
```
python3 generate_roam.py --clippings_path "E:\documents\My Clippings.txt"
```
If you want to use a different header for your Roam pages, save the header template to a text file and specify the path to this file with the `header_file` parameter:
```
python3 generate_roam.py --header_file "another_header.txt"
```
Upload resulting markdown files to Roam.
