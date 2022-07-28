New-PSDrive -Name ZA -PSProvider FileSystem -Root "C:\Users\Airlabs";
Set-Location -Path ZA:\;
cd script;
.\Scripts\Activate.ps1;
Start-Process python .\tv_on.py -Wait;
Start-Process python .\global_check.py;
deactivate;