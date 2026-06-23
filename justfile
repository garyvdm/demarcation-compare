setup: process-setup web-setup

[working-directory: 'web']
web-setup:
    npm install

[working-directory: 'web']
web-serve:
    npx vite --host desktop.vanhouse.net.za

[working-directory: 'web']
web-build:
    npx vite build

process-setup:
    uv sync

dw-data:
    # rm -r source-data/demarcations || true > /dev/null
    mkdir -p source-data/demarcations
    curl --fail --location --progress-bar --remote-header-name --remote-name-all --create-dirs --output-dir source-data -K source-data-urls

process-election-list:
    uv run elections.py

