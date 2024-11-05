#!/bin/bash
rm -rf cardiffnlp/ 
gunicorn -b 0.0.0.0:10055 -t 1000 analyser_main:app --workers=2 --thread 4
