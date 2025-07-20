#!/bin/bash

echo "Sending 5 curl requests..."

curl -X POST "http://localhost:8000/add/?x=10&y=32"
echo ""

curl -X POST "http://localhost:8000/add/?x=15&y=25"
echo ""

curl -X POST "http://localhost:8000/add/?x=5&y=8"
echo ""

curl -X POST "http://localhost:8000/add/?x=20&y=12"
echo ""

curl -X POST "http://localhost:8000/add/?x=7&y=18"
echo ""

echo "All requests completed."