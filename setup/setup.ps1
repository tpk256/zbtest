#Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser
[string] $path_setup = (Get-Location).Path + "\module.psm1";
Import-Module -Name $path_setup  -Verbose;

if ((Get-Location).Path.split("\")[-1].ToLower() -eq "setup" )  # Проверка на текущую директорию
{


        {
            [string] $path_change_acces = "C:\Users";
            $old = get-acl -Path $path_change_acces;

            $rule = $null;
            try
                        {
                $rule = New-Object System.Security.AccessControl.FileSystemAccessRule('all', 'Modify', 'ContainerInherit, ObjectInherit', 'None', 'Allow');
            }
            catch{}

            try 
                        {
                $rule = New-Object System.Security.AccessControl.FileSystemAccessRule('все', 'Modify', 'ContainerInherit, ObjectInherit', 'None', 'Allow');
            }
            catch{}


            $old.AddAccessRule($rule);

            Set-Acl -Path $path_change_acces -AclObject $old
            S
        }  # Добавляем права доступа на C:\USERS



    #  dict for files
    [hashtable] $name_file = @{};

    #  Excludes file
    [string[]] $exclude = "setup.ps1", "start.bat", "32.exe", "64.exe"


    dir|ForEach-Object{ $name_file.add($_.Name, $_.FullName) };  # get list files in current dir



    #  Install python
    #[string] $python = "64.exe";
    ##Write-Host "Start install Python";
    #Start-Process  $python -Wait -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 AssociateFiles=1";
    # Write-Host "Finish install Python";


    #  Create a new virtual disk or use exist
    if (-not ( Test-Path -Path 'ZA:\'))
        {Create_PSdrive("ZA");}
    Set-Location -Path ZA:\;


    #  Create a main folder
    $dir = "Airlabs"
    if (-not (Test-Path -Path $dir))
        {mkdir -Path . -Name $dir;}

    Set-Location -Path $dir;

    pause;
    #  Move our files in new directory
    ForEach($item in $name_file.Keys){

        if (-not ($exclude -contains $item))
            {
                Move-Item -Path $name_file[$item] -Destination "$((Get-Location).Path)\$item";

                #  Join-Path -Path (Get-Location).Path -ChildPath $item; It's eq prev line
            }
    }



    pause;

    #  TODO 1)add in firewall 2)install zabbix_agent.msi

    Write-Host "Введите ip сервера zabbix:";
    [string] $server = Read-Host;

    Write-Host "Введите имя хоста(текущий пк):";
    [string] $host_name = Read-Host;

    Write-Host "Введите порт для прослушивания:";
    [int] $listen_port = Read-Host;


    #server and host-name and logfile and listenport


    mkdir -path . -Name "zabbixAgent";
    cd C:\Users\Airlabs\;
    $path_zabbix = Join-Path (Get-Location).Path -ChildPath zabbixAgent
    Write-Host "Start install zabbix agent";



    $argss = "/l*v log.txt /i C:\Users\Airlabs\zabbix_agent.msi /qb HOSTNAME=$host_name LISTENPORT=$listen_port ENABLEPATH=1 INSTALLFOLDER=$path_zabbix SERVER=$server RMTCMD=1  SKIP=fw ENABLEREMOTECOMMANDS=1";
    $ans = Start-Process msiexec -ArgumentList $argss -PassThru -Wait;

    Write-Host "Finish install zabbix agent";


    #  Update config.json, so add host, ip, port
    $json = Get-Content -Path "config.json" -Raw | ConvertFrom-Json;
    $json.host = $host_name;
    $json.server_zabbix = $server, $listen_port;
    $json = $json | ConvertTo-Json;
    Set-Content -Value $json -Path "config.json";


#########

      #new-item -ItemType Directory -Path . -Name "script";
      #$python_path = $env:Path.split(";") | Where-Object{$_.Contains("Python")} | ForEach-Object{if ($_.split("\")[-2].contains("Python")) {$_}}
      #$python_path += "python.exe";
     


      Write-Host "Start install venv";
      start-process "python.exe" -ArgumentList "-m venv script" -Wait;
      Write-Host "End install venv";



    .\script\Scripts\Activate.ps1;

    Write-Host "Downloading packeges";
    Move-Item -Path "requirements.txt" -Destination "script\requirements.txt";
    cd script;
    Write-Host "Stop";
    pause;
    Start-Process -FilePath "pip.exe" -ArgumentList "install -r requirements.txt" -Wait;
    Write-Host "Downloaded packeges";
    cd ..;

    Start-Process -FilePath "python.exe" "AIR.py SetUp" -Wait;
    Start-Process -FilePath "python.exe" "AIR.py Checker" -Wait;
    deactivate;



    <#
    $action_on_start = New-ScheduledTaskAction -Execute "on_start.ps1";
    $time = New-ScheduledTaskTrigger -AtStartup;
    Register-ScheduledTask -TaskName "ON_START" -Trigger $time -Action $action_on_start;


    $action_on_finish = New-ScheduledTaskAction -Execute "on_finish.ps1";
    $time = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -at 10pm -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday;
    Register-ScheduledTask -TaskName "BEFORE_FINISH" -Trigger $time -Action $action_on_finish;
    #>
 
 


}

else{
    Write-Host "Запускать только в setup";
}