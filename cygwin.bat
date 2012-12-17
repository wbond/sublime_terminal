@echo off
%~d1
chdir %~p1
cd %1
bash --rcfile ~/.bashrc -i
