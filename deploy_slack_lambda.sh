#!/bin/bash
pip install git+https://github.com/nficano/python-lambda
lambda deploy \
  --config-file slack_lambda_config.yaml \
  --requirements slack_lambda_requirements.txt