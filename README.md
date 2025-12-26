# About
This repository presents an experiment for comparing three libraries for constraint-based testing in Python: Beartype, Icontract and Typeguard.

The project was prepared by Olesya A. Murzich as part of the Software Testing Methods course at SPbPU Institute of Computer Science and Cybersecurity (SPbPU ICSC).

# Authors and contributors
The main contributor of the project is Olesya A. Murzich, student of SPbPU ICSC.

The advisor of the projest is Vladimir A. Parkhomenko, senior lecturer of SPbPU ICSC. 

# Warranty
The contributors give no warranty for the using of the software.

# Licence
This program is open to use anywhere and is licensed under the GNU General Public License v3.0.

# Project structure
The project is a Windows console application. The instructions for it are located in the instructions.txt file. For dependency installation, it is recommended to run the installation/run_all_install.ps1 script to create a virtual environment for Python 3.11 (this version supports the correct functioning of all the libraries). It is also possible to install the required libraries listed in the file yourself using the list in requirements.txt.

After installing the libraries, it is possible to start generating incorrect data, checking the operation of functions, or analyzing the results.

The data/ folder contains one correct and one incorrect dataset, as well as a file for generating a new set of incorrect data.

The tools/ folder contains the source functions for testing and files for running the experiment once.

The experiments/ folder contains an analysis.py file to start analyzing the experimental results. Results will be saved in the experiments_incorrect.csv or experiments_normal.csv files each time the experiments are started. Additionally, the graphs created as a result of the data analysis are saved to the experiments/ folder.
