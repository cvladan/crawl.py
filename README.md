# Prepare

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

Run with default sitemap: python crawl.py
Specify custom sitemap: python crawl.py --sitemap <URL>