cd C:\Users\Airlabs\script;
.\Scripts\Activate.ps1;

cd ..;
Start-Process python "AIR.py OffTv" -Wait;
deactivate;
pause;
Start-Process powershell -ArgumentList "shutdown -s -t 60";
