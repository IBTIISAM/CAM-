#!/bin/sh

# Export LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

# Start the Flask app
exec python /app/FE.py