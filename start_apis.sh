#!/bin/bash
python3 -m controller.src.webhooks.api &
python3 -m controller.api.change_config &
wait