

@dw-data:
    # rm -r source-data/demarcations || true > /dev/null
    mkdir -p source-data/demarcations
    curl --fail --location --progress-bar --remote-header-name --remote-name-all --create-dirs --output-dir source-data -K source-data-urls
