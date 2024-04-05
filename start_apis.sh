#!/bin/bash
python3 -m controller.src.api.webhook &
python3 -m controller.src.api.change_config &
wait