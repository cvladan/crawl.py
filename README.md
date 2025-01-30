This Python script, `crawl.py`, is designed to crawl a website and generate Markdown files containing the content of each page. 

Here's a detailed explanation of how it works.


# Prepare System

```sh
# first run

asdf install python latest
asdf local python latest
python -m pip install --upgrade pip

asdf plugin add rust
asdf install rust latest
asdf local rust latest

# must do this (to the same version as local)
sdf global rust latest

# and actually not always the latest version
asdf install python 3.11.7
asdf global python 3.11.7
asdf local python 3.11.7
pip install --upgrade pip
```

```sh
# setup versions from .tool-versions
asdf install

# setup app
pip install -U crawl4ai
```

# Code

This is repo I'm replicating:

https://github.com/coleam00/ottomator-agents/blob/main/crawl4AI-agent/crawl4AI-examples/3-crawl_docs_FAST.py


# Usage

The script can be run in two ways:

1. **With the default sitemap**: `python crawl.py`
   - This will use the default sitemap specified in the script to crawl the website.

2. **With a custom sitemap**: `python crawl.py --sitemap <URL>`
   - Replace `<URL>` with the URL of the website you want to crawl.
   - This will use the provided URL as the starting point for crawling the website.

```sh
# Run with default sitemap:
python crawl.py

# Specify custom sitemap:
python crawl.py --sitemap <URL>
```

## How it Works

- The script first retrieves the sitemap (either the default or the provided custom URL) and extracts all the URLs from it.

- For each URL, the script fetches the HTML content of the corresponding web page.

    The script then extracts the main content from the HTML, removing any unwanted elements like navigation menus, headers, footers, etc.

    The extracted content is then saved to an individual Markdown file, with the filename based on the URL. For example, if the URL is `https://example.com/page1`, the Markdown file will be named `page1.md`.

- Additionally, the script appends the content of each page to a combined Markdown file named `combined.md`.

- The individual Markdown files are saved in the `crawls/` directory, while the `combined.md` file is saved in the current working directory.

