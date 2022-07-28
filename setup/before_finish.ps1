New-PSDrive -Name ZA -PSProvider FileSystem -Root "C:\Users\Airlabs";
Set-Location -Path ZA:\;
cd script;
.\Scripts\Activate.ps1;

Start-Process python .\remote_tv.py -Wait;

deactivate;
Start-Process powershell -ArgumentList "shutdown -s -t 60"